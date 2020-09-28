# https://pypi.org/project/routeros/#description
import paramiko
from datetime import datetime as dt
from routeros import login
from time import sleep
from transliterate import translit
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


def run_action(action, ip='', mac='', firm_name='', url=''):
    if action == 'check':
        return check(ip)
    if action == 'block':
        return block_ip(ip, block=True)
    if action == 'unblock':
        return block_ip(ip, block=False)
    if action == 'new_mac':
        return change_mac(ip, mac)
    if action == 'del':
        return del_ip(ip)
    if action == 'add':
        return add_ip(mac, firm_name, url)
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
    send_commands([command_string])
    sleep(1)
    return check(ip)


def change_mac(ip, mac):
    mac = get_mac(mac)
    if mac:
        commands = [f'ip dhcp-server lease set [find where address={ip}] mac-address={mac}',
                    f'ip arp set  [find where address={ip}] mac-address={mac}']
        send_commands(commands)
        message = 'Поменяно'
    else:
        message = 'Неправильный MAC'
    result = {'message': message}
    return result


def get_mac(mac):
    '''
    take string at input
    try to parse it to mac address
    return mac if success or False if not
    '''
    separators = (' ', ':', '-', '.')
    permitted_chars = set('0123456789abcdef')

    for separator in separators:
        mac = mac.replace(separator, '')
    mac = mac.lower()
    if len(mac) == 12 and set(mac) <= permitted_chars:
        return mac
    return False


def unique_mac(mac):
    return True


def send_commands(commands: list):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=IP,
                   username=LOGIN,
                   password=PASSWORD,
                   look_for_keys=False,
                   allow_agent=False)
    for command in commands:
        client.exec_command(command)


def find_free_ip() -> str:
    routeros = login(*connect_args)
    arp_records = routeros.query('/ip/arp/print').equal(
        interface='vlan_123',
        dynamic='false'
        )
    used_ip = set()
    ip_pool = set()

    for record in arp_records:
        used_ip.add(record.get('address'))
    for host in range(2, 256):
        ip_pool.add(f'193.238.176.{host}')
    for host in range(1, 255):
        ip_pool.add(f'193.238.177.{host}')

    free_ip = ip_pool - used_ip
    return free_ip.pop()


def add_ip(mac, firm_name, url):
    if not unique_mac(mac):
        message = ['Такой MAC уже существует']
        return {'message': message}

    mac = get_mac(mac)
    if mac:
        ip = find_free_ip()
        date = dt.now().strftime('%c')
        firm_name = translit(firm_name, 'ru', reversed=True)
        comment = f'"{date}; {firm_name}; {url}"'
        commands = [f'ip arp add address={ip} interface=vlan_123 mac-address={mac} comment={comment}',
                    f'ip dhcp-server lease add address={ip} mac-address={mac} comment={comment}',
                    f'ip firewall address-list add address={ip} list=ACL-ACCESS-CLIENTS comment={comment}']
        send_commands(commands)
        message = ['Готово :3', f'IP: {ip}']

    else:
        message = ['Неправильный  MAC']

    result = {'message': message}
    return result


def del_ip(ip):
    commands = [f'ip arp remove [find where address={ip}]',
                f'ip dhcp-server lease remove [find where address={ip}]',
                f'ip firewall address-list remove [find where address={ip}]']
    send_commands(commands)
    message = ['Удалил :b', f'IP: {ip}']
    result = {'message': message}
    return result
