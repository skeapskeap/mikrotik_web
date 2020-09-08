# https://pypi.org/project/routeros/#description
from routeros import login
from config import LOGIN, PASSWORD, IP, PORT

COMMAND_MAPPING = {
                   'arp': {'command': '/ip/arp/print', 'param': 'mac-address'},
                   'dhcp': {'command': '/ip/dhcp-server/lease/print', 'param': 'mac-address'},
                   'acl': {'command': '/ip/firewall/address-list/print', 'param': 'list'}
                   }
connect_args = [LOGIN, PASSWORD, IP, PORT, True]
ip_to_check = '193.238.176.6'


def mikrotik_query(ip: str, query_type: str) -> dict:
    command = COMMAND_MAPPING.get(query_type).get('command')
    param = COMMAND_MAPPING.get(query_type).get('param')
    routeros = login(*connect_args)
    reply = routeros.query(command).equal(address=ip, dynamic='false')

    if not reply:
        reply_message = 'no record found'
        error = True

    elif len(reply) > 1:
        reply_message = 'multiple records'
        error = True

    else:
        reply = reply[0]
        status = 'disabled' if reply.get('disabled') == 'true' else 'enabled'
        extra_param = reply.get(param)
        reply_message = dict(ip=ip, extra_param=extra_param, status=status)
        error = False

    result = dict(reply=reply_message, error=error)
    return result


def check_status(ip):
    arp = mikrotik_query(ip, 'arp')
    dhcp = mikrotik_query(ip, 'dhcp')
    acl = mikrotik_query(ip, 'acl')
    if arp['error'] or dhcp['error'] or acl['error']:
        status = False
    elif not arp['reply']['extra_param'] == dhcp['reply']['extra_param']:  # Проверка совпадения MAC из DHCP и ARP
        status = False
    else:
        status = True
    return dict(status=status,
                arp=arp['reply'],
                dhcp=dhcp['reply'],
                acl=acl['reply']
                )


if __name__ == '__main__':
    print(check_status(ip_to_check))
