import logging
import paramiko
import routeros_api
import routeros_api.exceptions as ros_exc
import mikrotik_app.config as cfg
from datetime import datetime as dt
from logging import handlers

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


def ros_api():
    try:
        connection = routeros_api.RouterOsApiPool(
                                    cfg.IP,
                                    **cfg.ROS_API_KWARGS)
        api = connection.get_api()
        return api
    except ros_exc.RouterOsApiConnectionError:
        logger.error("ROS_API Connection fail")
        return False


def send_commands(commands: list):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(**cfg.SSH_KWARGS)
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
        mac = ':'.join(
            [mac[:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:12]]
            )
        return mac
    else:
        return False


def find_free_ip() -> str:
    try:
        all_records = ros_api().get_resource('/ip/arp')
        arp_in_vlan = all_records.get(interface='vlan_123',
                                      dynamic='false')
    # API микротика не переваривает reply, содержащий non-ascii символы =\
    # В некоторых хостах такие символы есть, например поле Comment
    except ValueError:
        logger.info("Invalid ARP reply about")
        return False

    used_ip = set()
    ip_pool = set()

    for record in arp_in_vlan:
        used_ip.add(record.get('address'))
    for host in range(2, 256):
        ip_pool.add(f'{cfg.SUBNET_1}{host}')
    for host in range(1, 255):
        ip_pool.add(f'{cfg.SUBNET_2}{host}')

    free_ip_pool = ip_pool - used_ip

    while free_ip_pool:
        # Из разности множеств выбирается рандомный IP
        free_ip = free_ip_pool.pop()
        # Проверка, что свободный IP не фигурирует в dhcl-list и acl
        try:
            all_dhcp = ros_api().get_resource('/ip/dhcp-server/lease')
            all_acl = ros_api().get_resource('/ip/firewall/address-list')
            dhcp_used = all_dhcp.get(address=free_ip, dynamic='false')
            acl_used = all_acl.get(address=free_ip, dynamic='false')
            if not (dhcp_used or acl_used):
                return free_ip
        # API микротика не переваривает reply, содержащий non-ascii символы =\
        # В некоторых хостах такие символы есть, например поле Comment
        except ValueError:
            logger.error(f"Invalid reply about {free_ip}")
            continue
    return False


if __name__ == '__main__':
    print(ros_api())
