# https://pypi.org/project/routeros/#description
import paramiko
from time import sleep
from routeros import login
from .config import LOGIN, PASSWORD, IP, PORT

connect_args = [LOGIN, PASSWORD, IP, PORT, True]


class AboutIP:

    def __init__(self, ip):
        self.ip = ip
        self.arp = self.query('/ip/arp/print')
        self.dhcp = self.query('/ip/dhcp-server/lease/print')
        self.acl = self.query('/ip/firewall/address-list/print')

    def __repr__(self):
        return f'<AboutIP: {self.ip}>'

    def query(self, query) -> tuple:
        routeros = login(*connect_args)
        reply = routeros.query(query).equal(address=self.ip, dynamic='false')
        if not reply:
            return False
        return reply

    def multiple_records(self) -> bool:
        if self.arp and len(self.arp) > 1:
            return True
        if self.dhcp and len(self.dhcp) > 1:
            return True
        if self.acl and len(self.acl) > 1:
            return True
        return False

    def all_records_found(self) -> bool:
        if self.arp and self.dhcp and self.acl:
            return True

    def same_mac(self) -> bool:
        try:
            arp_mac = self.arp[0].get('mac-address')
            dhcp_mac = self.dhcp[0].get('mac-address')
        except (TypeError, IndexError):
            return False
        if arp_mac == dhcp_mac:
            return True

    def all_active(self) -> bool:
        try:
            arp_disabled = self.arp[0].get('disabled')
            dhcp_disabled = self.dhcp[0].get('disabled')
            acl_disabled = self.acl[0].get('disabled')
            acl_list = self.acl[0].get('list')
        except (TypeError, IndexError):
            return False

        if arp_disabled == 'false' \
                and dhcp_disabled == 'false' \
                and acl_disabled == 'false' \
                and acl_list == 'ACL-ACCESS-CLIENTS':
            return True
        else:
            return False

    def summary_check(self) -> bool:
        if self.multiple_records():
            return False

        if not self.all_records_found():
            return False

        if not self.all_active():
            return False

        return True

    def parse_arp(self):
        records = []
        for item in self.arp:
            ip = item.get('address')
            mac = item.get('mac-address')
            state = 'enabled' if item.get('disabled') == 'false' else 'disabled'
            records.append(f'IP={ip}, MAC={mac}, state={state}')
        return records

    def parse_dhcp(self):
        records = []
        for item in self.dhcp:
            ip = item.get('address')
            mac = item.get('mac-address')
            state = 'enabled' if item.get('disabled') == 'false' else 'disabled'
            status = item.get('status')
            records.append(f'IP={ip}, MAC={mac}, status={status}, state={state}')
        return records

    def parse_acl(self):
        records = []
        for item in self.acl:
            ip = item.get('address')
            access_list = item.get('list')
            state = 'enabled' if item.get('disabled') == 'false' else 'disabled'
            records.append(f'IP={ip}, ACL={access_list}, state={state}')
        return records


def run_action(ip, action, mac):
    if action == 'check':
        return check(ip)
    if action == 'block':
        return block_ip(ip, block=True)
    if action == 'unblock':
        return block_ip(ip, block=False)
    if action == 'new_mac':
        return change_mac(ip, mac)
    if action == 'delete_ip':
        pass
    if action == 'new_ip':
        pass
    else:
        return {'message': 'unknown command'}


def check(ip):
    about_ip = AboutIP(ip)

    if about_ip.arp:
        arp = about_ip.parse_arp()
    else:
        arp = ['no records found']

    if about_ip.dhcp:
        dhcp = about_ip.parse_dhcp()
    else:
        dhcp = ['no records found']

    if about_ip.acl:
        acl = about_ip.parse_acl()
    else:
        acl = ['no records found']

    message = 'Всё хорошо' if about_ip.summary_check() else 'Не всё хорошо'

    result = {'arp': arp,
              'dhcp': dhcp,
              'acl': acl,
              'message': message}
    return result


def block_ip(ip, block=True):
    if block:
        action = 'disable'
    else:
        action = 'enable'
    ip = ip.strip()
    command_string = f'ip arp {action} [find where address={ip}]'
    send_command(command_string)
    sleep(1)
    return check(ip)


def change_mac(ip, mac):
    mac = get_mac(mac)
    if mac:
        commands = [f'ip dhcp-server lease set [find where address={ip}] mac-address={mac}',
                    f'ip arp set  [find where address={ip}] mac-address={mac}']
        for command in commands:
            send_command(command)
        message = 'Поменяно'
    else:
        message = 'Неправильный MAC'
    result = {'message': message}
    return result


def get_mac(mac):
    separators = (' ', ':', '-', '.')
    permitted_chars = set('0123456789abcdef')

    for separator in separators:
        mac = mac.replace(separator, '')
    mac = mac.lower()
    if len(mac) == 12 and set(mac) <= permitted_chars:
        return mac
    return False


def send_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=IP,
                   username=LOGIN,
                   password=PASSWORD,
                   look_for_keys=False,
                   allow_agent=False)
    client.exec_command(command)
