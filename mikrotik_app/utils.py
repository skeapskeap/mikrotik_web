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
