#!/usr/bin/env python3
"""Get Redis master IP. Used by ansible to update redisdb hosts."""

import argparse
import socket
import re

import common_redis as common


def get_current_master(db):
    """Get current master."""
    redis_conf = f'/opt/redis/{db}/redis.conf'

    with open(redis_conf, 'r') as conf:
        for line in conf.readlines():
            if 'requirepass' in line:
                password = line.split(' ')[1].rstrip()
            if 'port' == line.split(' ')[0]:
                sentinel_port = int(line.split(' ')[1]) - 20000

    redis_obj = common.Redis(False, verbose=False, timeout=1)
    fqdn = socket.gethostbyaddr(socket.gethostname())[0]

    hostname = fqdn.split('.')[0]

    ext = ''
    if len(fqdn.split('.')) > 1:
        ext = '.' + '.'.join(fqdn.split('.')[1:])

    # Query sentinel
    for each in ["{{ instances['srv1'] }}", "{{ instances['srv2'] }}", "{{ instances['srv3'] }}"]:
        master_ip = redis_obj.run_command(each, sentinel_port, password, 'SENTINEL GET-MASTER-ADDR-BY-NAME default')
        if master_ip:
            break

    if not master_ip:
        # Fallback to IP of srv1.
        master_ip = "{{ instances['srv1'] }}"
    else:
        master_ip = master_ip[0].decode()

    print(master_ip)


def main():
    """Main."""
    parser = argparse.ArgumentParser(description='Get Redis master IP')
    parser.add_argument('--db', '-d', help='redis db name', required=True)
    args = parser.parse_args()

    get_current_master(args.db)


if __name__ == '__main__':
    main()
