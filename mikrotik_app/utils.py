import logging
import paramiko
from .config import LOGIN, PASSWORD, IP, connect_args
from routeros import login
from datetime import datetime as dt

logging.basicConfig(filename='log', level=logging.INFO)


def mikrotik():
    return login(*connect_args)


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


def time_now():
    time = dt.now().strftime('%c')
    return time


def write_log(request):
    data = dict(request.POST)
    del data['csrfmiddlewaretoken']
    logging.info(f"{time_now()}; User {request.user} POSTed: {data}")


if __name__ == '__main__':
    print(find_free_ip())