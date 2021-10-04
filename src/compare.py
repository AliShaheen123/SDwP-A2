import sys
import time
from tabulate import tabulate
import os


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('usage: compare.py [files]')
        exit(0)
    duration_dict = {}
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    for i in range(1, len(args)):
        try:
            st = time.time()
            exec(open(args[i]).read())
            end = time.time()
            duration_dict[args[i]] = end - st
        except Exception as e:
            print(f"The following exception raised while executing the file {args[i]}: {e}")
            continue
    sys.stdout = old_stdout
    duration_list = list(duration_dict.items())
    duration_list.sort(key=lambda x: x[1])
    duration_table = [['PROGRAM', 'RANK', 'TIME ELAPSED']] + \
                     [[duration_list[i][0], i + 1, "{:.7f}s".format(duration_list[i][1])] for i in range(len(duration_list))]
    print(tabulate(duration_table))
