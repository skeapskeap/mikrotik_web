import logging
import paramiko
from .config import SSH_KWARGS, ROS_API_ARGS, SUBNET_1, SUBNET_2
from datetime import datetime as dt
from logging import handlers
from routeros import login
from routeros.exc import ConnectionError, FatalError

handler = handlers.RotatingFileHandler(
    filename='log', maxBytes=512_000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s; %(levelname)s; %(name)s; %(message)s', '%c')
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger()


def time_now():
    time = dt.now().strftime('%c')
    return time


def write_log(request):
    data = dict(request.POST)
    del data['csrfmiddlewaretoken']
    logger.info(f"User {request.user} POSTed: {data}")


def mikrotik():
    try:
        return login(*ROS_API_ARGS)
    except (ConnectionError, ConnectionRefusedError, FatalError):
        logger.error("ROS_API Connection fail")
        return False


def send_commands(commands: list):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(**SSH_KWARGS)
            for command in commands:
                ssh.exec_command(command)
            return True
        except paramiko.ssh_exception.SSHException:
            logger.error("SSH connection fail")
            return False


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
    try:
        arp_records = mikrotik().query('/ip/arp/print').equal(
            interface='vlan_123',
            dynamic='false')
    # API микротика не переваривает reply, содержащий non-ascii символы =\
    # В некоторых хостах такие символы есть, например поле Comment
    except ValueError:
        logger.info("Invalid ARP reply about")
        return False

    used_ip = set()
    ip_pool = set()

    for record in arp_records:
        used_ip.add(record.get('address'))
    for host in range(2, 256):
        ip_pool.add(f'{SUBNET_1}{host}')
    for host in range(1, 255):
        ip_pool.add(f'{SUBNET_2}{host}')

    free_ip_pool = ip_pool - used_ip

    while free_ip_pool:
        # Из разности множеств выбирается рандомный IP
        free_ip = free_ip_pool.pop()
        # Проверка, что свободный IP не фигурирует в dhcl-list и acl
        try:
            dhcp_used = mikrotik().query('/ip/dhcp-server/lease/print').equal(address=free_ip, dynamic='false')
            acl_used = mikrotik().query('/ip/firewall/address-list/print').equal(address=free_ip, dynamic='false')
            if not (dhcp_used or acl_used):
                return free_ip
        # API микротика не переваривает reply, содержащий non-ascii символы =\
        # В некоторых хостах такие символы есть, например поле Comment
        except ValueError:
            logger.error(f"Invalid reply about {free_ip}")
            continue
    return False


if __name__ == '__main__':
    print(find_free_ip())
