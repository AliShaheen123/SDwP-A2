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
    help_mes = "usage: bc.py action [-flag value]*\n" + \
               "This program ...\n" + \
               "compile\n" + \
               "\t-py file.py compile file into bytecode and store it as file.pyc\n" + \
               "\t-s \"src\" compile src into bytecode and store it as out.pyc\n" + \
               "print\n" + \
               "\t-py src.py produce human-readable bytecode from python file\n" + \
               "\t-pyc src.pyc produce human-readable bytecode from compiled .pyc file\n" + \
               "\t-s \"src\" produce human-readable bytecode from normal string\n" + \
               "compare -format src [-format src]+\n" + \
               "\tproduce bytecode comparison for giving sources\n" + \
               "\t(supported formats -py, -pyc, -s)\n"

    if len(args) == 1:
        print(help_mes)
        exit(0)

    if args[1] == 'print':
        if args[2] not in ['-py', '-pyc', '-s']:
            print(help_mes)
            exit(0)
        try:
            if args[2] == '-py':
                code = get_code_py(args[3])
            elif args[2] == '-pyc':
                code = get_code_pyc(args[3])
            else:
                code = compile(args[3], '', 'exec')
            output = get_rec(code)
            for item in output:
                print(item[0], item[1])
        except Exception as e:
            print(f"The following exception raised while handling the file {args[3]}: {e}")

    elif args[1] == 'compile':
        if args[2] not in ['-py', '-s']:
            print(help_mes)
            exit(0)

        try:
            if args[2] == '-py':
                cfile = args[3] + 'c'
                py_compile.compile(args[3], cfile)
            else:
                cfile = 'out.pyc'
                temp_name = 'temp_file.py'
                temp_file = open(temp_name, 'w')
                temp_file.write(args[3] + '\n')
                temp_file.close()
                py_compile.compile(temp_name, cfile)
                os.remove(temp_name)
        except Exception as e:
            print(f"The following exception raised while handling the file {args[3]}: {e}")

    elif args[1] == 'compare':
        if args[2] not in ['-py', '-pyc', '-s']:
            print(help_mes)
            exit(0)
        table_dict = []
        columns_label = []
        for i in range(3, len(args), 2):
            columns_label.append(args[i])
            table_dict.append({})
            try:
                if args[i - 1] == '-py':
                    code = get_code_py(args[i])
                elif args[i - 1] == '-pyc':
                    code = get_code_pyc(args[i])
                else:
                    code = compile(args[i], '', 'exec')
                output = get_rec(code)
                for item in output:
                    if table_dict[-1].get(item[0]) is None:
                        table_dict[-1][item[0]] = 0
                    table_dict[-1][item[0]] += 1
            except Exception as e:
                print(f"The following exception raised while handling the file {args[i]}: {e}")
        rows_labels = list(set(key for dict_i in table_dict for key in dict_i.keys()))
        rows = [[label] + [0 if dict_i.get(label) is None else dict_i[label] for dict_i in table_dict] for label in rows_labels]
        print(tabulate(rows, headers=columns_label))
        old_stdout = sys.stdout
        res_file = open('results.txt', 'w')
        sys.stdout = res_file
        print(tabulate(rows, headers=columns_label))
        sys.stdout = old_stdout

    else:
        print(help_mes)
        exit(0)
