# https://pypi.org/project/routeros/#description
from routeros import login
from config import LOGIN, PASSWORD, IP, PORT

connect_args = [LOGIN, PASSWORD, IP, PORT, True]


class AboutIP:

    def __init__(self, ip):
        self.ip = ip

    def __repr__(self):
        return f'<AboutIP: {self.ip}>'

    def query(self, query) -> tuple:
        routeros = login(*connect_args)
        reply = routeros.query(query).equal(address=self.ip, dynamic='false')
        return reply

    def arp(self) -> tuple:
        reply = self.query('/ip/arp/print')
        if not reply:
            return False
        return reply

    def dhcp(self) -> tuple:
        reply = self.query('/ip/dhcp-server/lease/print')
        if not reply:
            return False
        return reply

    def acl(self) -> tuple:
        reply = self.query('/ip/firewall/address-list/print')
        if not reply:
            return False
        return reply

    def multiple_records(self) -> bool:
        if self.arp() and len(self.arp()) > 1:
            return True
        if self.dhcp() and len(self.dhcp()) > 1:
            return True
        if self.acl() and len(self.acl()) > 1:
            return True
        return False

    def all_records_found(self) -> bool:
        if self.arp() and self.dhcp() and self.acl():
            return True

    def same_mac(self) -> bool:
        try:
            arp_mac = self.arp()[0].get('mac-address')
            dhcp_mac = self.dhcp()[0].get('mac-address')
        except (TypeError, IndexError):
            return False
        if arp_mac == dhcp_mac:
            return True

    def all_active(self) -> bool:
        try:
            arp_state = self.arp()[0].get('disabled')
            dhcp_state = self.dhcp()[0].get('disabled')
            acl_state = self.acl()[0].get('disabled')
            acl_list = self.acl()[0].get('list')
        except (TypeError, IndexError):
            return False
        if arp_state == 'false' \
                and dhcp_state == 'false' \
                and acl_state == 'false' \
                and acl_list == 'ACL-ACCESS-CLIENTS':
            return True

    def summary_check(self) -> bool:
        if self.multiple_records():
            return False

        if not self.all_records_found():
            return False

        if self.all_active():
            return True

        return False
