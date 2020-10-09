# https://pypi.org/project/routeros/#description
from .decorators import proper_mac, unique_mac
from .utils import find_free_ip, mikrotik, send_commands, time_now
from time import sleep
from transliterate import translit


class AboutIP:

    def __init__(self, ip):
        self.ip = ip
        self.arp = self.query('/ip/arp/print')
        self.dhcp = self.query('/ip/dhcp-server/lease/print')
        self.acl = self.query('/ip/firewall/address-list/print')

    def __repr__(self):
        return f'<AboutIP: {self.ip}>'

    def query(self, query) -> tuple:
        reply = mikrotik().query(query).equal(address=self.ip, dynamic='false')
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


def run_action(**kwargs):
    action      = kwargs.get('action')
    ip          = kwargs.get('ip')
    mac         = kwargs.get('mac')
    firm_name   = kwargs.get('firm_name')
    url         = kwargs.get('url')

    if action == 'check':
        return check(ip)
    if action == 'block':
        return block_ip(ip, block=True)
    if action == 'unblock':
        return block_ip(ip, block=False)
    if action == 'update':
        return update_data(ip=ip, mac=mac, firm_name=firm_name, url=url)
    if action == 'del':
        return del_ip(ip)
    if action == 'add':
        return add_ip(mac=mac, firm_name=firm_name, url=url)
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

    message = ['Всё хорошо'] if about_ip.summary_check() else ['Не всё хорошо']

    result = {'arp': arp,
              'dhcp': dhcp,
              'acl': acl,
              'message': [message]}
    return result


def block_ip(ip, block=True):
    if block:
        action = 'disable'
    else:
        action = 'enable'
    ip = ip.strip()
    commands = [f'ip arp {action} [find where address={ip}]',
                f'ip dhcp-server lease {action} [find where address={ip}]',
                f'ip firewall address-list {action} [find where address={ip}]']
    send_commands(commands)
    sleep(1)
    return check(ip)


@proper_mac
@unique_mac
def update_data(**kwargs):
    ip, mac, firm_name, url = kwargs.values()
    commands = []
    if mac:
        commands.extend([f'ip dhcp-server lease set [find where address={ip}] mac-address={mac}',
                         f'ip arp set  [find where address={ip}] mac-address={mac}'])
    if firm_name or url:
        firm_name = translit(firm_name, 'ru', reversed=True)
        comment = f'"{time_now()}; {firm_name}; {url}"'
        commands.extend([f'ip dhcp-server lease set [find where address={ip}] comment={comment}',
                         f'ip arp set  [find where address={ip}] comment={comment}',
                         f'ip firewall address-list set  [find where address={ip}] comment={comment}'])

    send_commands(commands)
    result = {'message': ['Поменяно', commands]}
    return result


@proper_mac
@unique_mac
def add_ip(**kwargs):
    mac, firm_name, url = kwargs.values()

    ip = find_free_ip()
    firm_name = translit(firm_name, 'ru', reversed=True)
    comment = f'"{time_now()}; {firm_name}; {url}"'
    commands = [f'ip arp add address={ip} interface=vlan_123 mac-address={mac} comment={comment}',
                f'ip dhcp-server lease add address={ip} mac-address={mac} comment={comment}',
                f'ip firewall address-list add address={ip} list=ACL-ACCESS-CLIENTS comment={comment}']

    send_commands(commands)
    result = {'message': [f'Добавлен IP: {ip}', commands]}
    return result


def del_ip(ip):
    commands = [f'ip arp remove [find where address={ip}]',
                f'ip dhcp-server lease remove [find where address={ip}]',
                f'ip firewall address-list remove [find where address={ip}]']
    send_commands(commands)
    result = {'message': [f'Удалён IP: {ip}', commands]}
    return result
