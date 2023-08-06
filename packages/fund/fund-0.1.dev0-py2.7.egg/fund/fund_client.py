#!/usr/bin/env python
#coding:utf-8
"""
  Author:  yafeile --<yafeile@sohu.com>
  Purpose: 
  Created: Friday, April 20, 2018
"""

import socket
from msgpack import unpackb
from functools import wraps
from datetime import datetime
from decimal import Decimal

def decode_data(raw):
    data = unpackb(raw)
    result = []
    for d in data:
        arr = []
        _d = d[0]
        _d = datetime.strptime(_d, '%Y-%m-%d').date()
        arr.append(_d)
        _remain = d[1:]
        for r in _remain:
            r = Decimal(str(r))
            arr.append(r)
        result.append(arr)
    return result

def create_socket():
    sock = socket.socket()
    sock.connect(('193.112.55.231',8000))
    return sock


def run_command(func):
    @wraps(func)
    def _wrapper(*args):
        fund_id = args[0]
        if isinstance(fund_id, str):
            l = len(fund_id)
            if l == 6:
                command = func(*args)
                return run(command)
            else:
                raise Exception('The given fund_id is wrong.')
        else:
            raise Exception("fund_id must be str.")
    return _wrapper

@run_command
def get(fund_id,num=30):
    """
    获取指定基金的最近数据
    """
    command = ['GET', fund_id, str(num)]
    return ' '.join(command)

@run_command
def history(fund_id):
    """
    获取指定基金的历史数据
    """
    if isinstance(fund_id, str):
        l = len(fund_id)
        if l == 6:
            command = ['HISTORY', fund_id]
            command = ' '.join(command)
            return command
        else:
            raise Exception('The given fund_id is wrong.')
    else:
        raise Exception("fund_id must be str.")

def run(cmd):
    bulk = 1024
    sock = create_socket()
    ret = sock.recv(bulk)
    if ret == 'HELLO':
        sock.send(cmd)
        data = []
        while 1:
            raw_data = sock.recv(bulk)
            l = len(raw_data)
            data.append(raw_data)
            if l < bulk:
                break
        data = ''.join(data)
        data = decode_data(data)
        return data
    else:
        raise Exception("Can not connect to the server.")
    
def main():
    test = get('000009')
    print(test)


if __name__ == '__main__':
    main()