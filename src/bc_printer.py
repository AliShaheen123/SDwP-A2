import dis
import marshal
import struct
import sys
import time
from types import CodeType

from tabulate import tabulate
import os
import py_compile


def get_code_py(path):
    content = ''
    file = open(path, 'r')
    lines = file.readlines()
    for line in lines:
        content += line
    return compile(content, '', 'exec')


def get_code_pyc(path):
    file = open(path, 'rb')

    magic = file.read(4)
    bit_field = None
    timestamp = None
    hashstr = None
    size = None

    if sys.version_info.major == 3 and sys.version_info.minor >= 7:
        bit_field = int.from_bytes(file.read(4), byteorder=sys.byteorder)
        if 1 & bit_field == 1:
            hashstr = file.read(8)
        else:
            timestamp = file.read(4)
            size = file.read(4)
            size = struct.unpack('I', size)[0]
    elif sys.version_info.major == 3 and sys.version_info.minor >= 3:
        timestamp = file.read(4)
        size = file.read(4)
        size = struct.unpack('I', size)[0]
    else:
        timestamp = file.read(4)
    return marshal.load(file)


def get_rec(code):
    bytecode = dis.get_instructions(code)
    ret = []
    for instr in bytecode:
        if type(instr.argval) == CodeType:
            temp = get_rec(instr.argval)
            ret += temp
        ret.append((instr.opname, instr.argval))
    return ret


if __name__ == '__main__':
    args = sys.argv
    help_mes = "usage: bc.py [-flag value]*\n" + \
               "This program ...\n" + \
               "\t-py src.py produce human-readable bytecode from python file\n" + \
               "\t-pyc src.pyc produce human-readable bytecode from compiled .pyc file\n" + \
               "\t-s \"src\" produce human-readable bytecode from normal string"

    if len(args) == 1:
        print(help_mes)
        exit(0)

    if args[1] not in ['-py', '-pyc', '-s']:
        print(help_mes)
        exit(0)
    try:
        if args[1] == '-py':
            code = get_code_py(args[2])
        elif args[1] == '-pyc':
            code = get_code_pyc(args[2])
        else:
            code = compile(args[2], '', 'exec')
        output = get_rec(code)
        for item in output:
            print(item[0], item[1])
    except Exception as e:
        print(f"The following exception raised while handling the file {args[2]}: {e}")
