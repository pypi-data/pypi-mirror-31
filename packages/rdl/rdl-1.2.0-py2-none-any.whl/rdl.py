#!/usr/bin/env python
# coding=utf-8

import os
import sys
import redis
import base64
import argparse


__version__ = '1.2.0'


PY2 = sys.version_info.major == 2


BUF_LIMIT = 1024 * 2
WRITE_MODE = 'wb'
AWRITE_MODE = 'ab'


if PY2:
    WRITE_MODE = 'w'
    AWRITE_MODE = 'a'


def write_file(file_name, buf, initial=False):
    """
    :param bytes buf: buffer to write, in python2 it's type would be str
    """
    if initial:
        mode = WRITE_MODE
        if os.path.exists(file_name):
            print('==> Warning: {} will be covered!'.format(file_name))
    else:
        print('==> Writing {}, chunk size {}'.format(file_name, len(buf)))
        mode = AWRITE_MODE

    with open(file_name, mode) as f:
        f.write(buf)


def print_loop(loop, clear=True):
    s = '==> processed keys: {}'.format(loop)

    if clear:
        sys.stdout.write(s)
        sys.stdout.flush()
        sys.stdout.write(len(s) * '\b')
    else:
        print(s)


def get_client(n, host=None, port=None, password=None):
    if hasattr(redis, 'StrictRedis'):
        client_class = redis.StrictRedis
    else:
        # Backward compatibility
        client_class = redis.Redis
    kwargs = {}
    if host:
        kwargs['host'] = host
    if port:
        kwargs['port'] = port
    if password:
        kwargs['password'] = password
    db = client_class(db=n, **kwargs)
    print('==> Use redis {}:{}/{}'.format(host or '<default host>', port or '<default port>', n))
    # TODO show db info
    return db


def dump(file_name, db, ignore_none_value=False):
    buf = b''
    loop = 0
    initial_write = True

    # NOTE KEYS may ruin performance when it is executed against large databases.
    # SCAN can be used in production without the downside of commands like KEYS
    for k in db.scan_iter():
        # `k`is bytes for python3, str for python2

        # dump() returns bytes for python3, str for python2
        v = db.dump(k)

        if v is None:
            msg = 'got None when DUMP key `{}`'.format(k)
            if ignore_none_value:
                print('{}, ignore'.format(msg))
                continue
            else:
                raise ValueError(msg)

        # form the line
        line = k + b'\t' + base64.b64encode(v) + b'\n'
        buf += line
        loop += 1

        if loop % BUF_LIMIT == 0:
            write_file(file_name, buf, initial_write)
            print_loop(loop)
            # Clear buf
            buf = b''
            initial_write = False

    # In case of not reach limit
    if buf:
        write_file(file_name, buf, initial_write)
        print_loop(loop, False)

    if not loop:
        print('Empty db, nothing happened')
        return


def load(file_name, db, f):
    if f:
        print('==> Flush database!')
        db.flushdb()

    with open(file_name, 'r') as f:
        loop = 0
        for line in f:
            k, v = tuple(line.split('\t'))
            v = base64.b64decode(v)
            db.restore(k, 0, v)

            loop += 1
            if loop % BUF_LIMIT == 0:
                print_loop(loop)

        print_loop(loop, False)


def main():
    parser = argparse.ArgumentParser(description="Redis dump-load tool.", add_help=False)
    parser.add_argument('action', metavar="ACTION", type=str, choices=['dump', 'load'], help="`dump` or `load`.")
    parser.add_argument('file_name', metavar="FILE", type=str, help="if action is dump, then its output file, if actions is load, then its source file.")
    parser.add_argument('-n', type=int, default=0, help="Number of database to process.")
    parser.add_argument('-h', '--host', type=str, help="Redis host")
    parser.add_argument('-p', '--port', type=int, help="Redis port")
    parser.add_argument('-a', '--auth', type=str, help="Redis password")
    parser.add_argument('-f', '--flushdb', action='store_true', help="Force or flush database before load")
    parser.add_argument('--ignore-none-value', action='store_true', help="Ignore None when dumping db, by default it will raise ValueError if DUMP result is None")
    parser.add_argument('--help', action='help', help="show this help message and exit")
    # --version
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()

    db = get_client(args.n, args.host, args.port, args.auth)

    if 'dump' == args.action:
        dump(args.file_name, db, args.ignore_none_value)
    else:  # load
        load(args.file_name, db, args.flushdb)


if __name__ == '__main__':
    main()
