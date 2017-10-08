# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-10-08 15:01:56
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-10-08 17:34:50

from sys import argv
import battle_tested as bt
import argparse

parser = argparse.ArgumentParser(prog='__main__.py')

parser.add_argument(
    '--fuzz',
    help="send the fuzzer's output to stdout",
    action='store_true'
)
parser.add_argument(
    '--test',
    help="run tests to see if battle_tested works correctly on you system",
    action='store_true'
)
parser.add_argument(
    '--benchmark',
    help="test how fast battle_tested can run on your system",
    action='store_true'
)

if '__main__.py' in argv[-1] or 'help' in argv:
    parsed = parser.parse_args(['-h'])

args, unknown = parser.parse_known_args()

def runs_in_window(time_window=1):
    def counter(a,b):
        counter.c += 1
    counter.c = 0
    bt.fuzz(counter, quiet=True, seconds=time_window)
    return counter.c

if args.benchmark:
    print('running benchmarks now')
    for i in [1,3,6,15,30,60]:
        print('{} seconds {} tests'.format(i,runs_in_window(i)))
if args.fuzz:
    for i in bt.multiprocess_garbage():
        try:
            print(i)
        except:
            pass
if args.test:
    print('running battle_tested.run_tests')
    bt.run_tests()
