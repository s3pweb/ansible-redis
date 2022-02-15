#!/usr/bin/env python3
"""Get Redis master IP. Used by ansible to update redisdb hosts."""

import argparse
import socket

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
    hostname = socket.gethostname()

    prefix = hostname.split('.')[0]
    prefix = ''.join([i for i in prefix if not i.isdigit()])

    ext = ''
    if len(hostname.split('.')) > 1:
        ext = '.' + '.'.join(hostname.split('.')[1:])

    # Query sentinel
    for i in range(1, 4):
        host = prefix + str(i) + ext
        master_ip = redis_obj.run_command(host, sentinel_port, password, 'SENTINEL GET-MASTER-ADDR-BY-NAME default')
        if master_ip:
            break

    if not master_ip:
        # Return the IP of the first db, usually srv1.
        master_ip = socket.gethostbyname(prefix + '1' + ext)
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
