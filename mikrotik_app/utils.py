import logging
import paramiko
from .config import SSH_KWARGS, ROS_API_ARGS, SUBNET_1, SUBNET_2
from routeros import login
from routeros.exc import ConnectionError, FatalError
from datetime import datetime as dt

logging.basicConfig(filename='log', level=logging.INFO)


def mikrotik():
    try:
        return login(*ROS_API_ARGS)
    except (ConnectionError, ConnectionRefusedError, FatalError):
        logging.info(f"{time_now()}; ROS_API Connection fail")
        return False


def send_commands(commands: list):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(**SSH_KWARGS)
    for command in commands:
        client.exec_command(command)


def proper_mac(mac):
    '''
    take a string from input
    try to parse it to mac address
    return mac if success or False if not
    '''
    mac = mac.strip().lower()
    separators = (' ', ':', '-', '.')
    permitted_chars = set('0123456789abcdef')

    for separator in separators:
        mac = mac.replace(separator, '')

    if len(mac) == 12 and set(mac) <= permitted_chars:
        mac = mac.upper()
        mac = ':'.join([ mac[:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:12] ])
        return mac
    else:
        return False


def find_free_ip() -> str:
    arp_records = mikrotik().query('/ip/arp/print').equal(
        interface='vlan_123',
        dynamic='false')

    used_ip = set()
    ip_pool = set()

    for record in arp_records:
        used_ip.add(record.get('address'))
    for host in range(2, 256):
        ip_pool.add(f'{SUBNET_1}{host}')
    for host in range(1, 255):
        ip_pool.add(f'{SUBNET_2}{host}')

    # Из разности множеств выбирается рандомный IP
    free_ip_pool = ip_pool - used_ip

    while True:
        free_ip = free_ip_pool.pop()
        print(f'free_ip_pool {free_ip_pool}')
        print(f'free_ip {free_ip}')
        # Проверка, что свободный IP не фигурирует в dhcl-list и acl
        dhcp_used = mikrotik().query('/ip/dhcp-server/lease/print').equal(address=free_ip, dynamic='false')
        acl_used = mikrotik().query('/ip/firewall/address-list/print').equal(address=free_ip, dynamic='false')
        if not (dhcp_used or acl_used):
            return free_ip


def time_now():
    time = dt.now().strftime('%c')
    return time


def write_log(request):
    data = dict(request.POST)
    del data['csrfmiddlewaretoken']
    logging.info(f"{time_now()}; User {request.user} POSTed: {data}")


if __name__ == '__main__':
    print(find_free_ip())