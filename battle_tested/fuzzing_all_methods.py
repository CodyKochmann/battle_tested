from battle_tested import *
def test(a):
    try:
        len(bool(a))
        len(a)
    except Exception:
        pass
fuzz(test)
fuzz(test)
def test(a):
    len(bool(a))
fuzz(test)
from sqlitedict import SqliteDict

def harness(key, value):
    """ this tests what can be assigned in SqliteDict's keys and values """
    mydict = SqliteDict(":memory:")
    mydict[key] = value

from battle_tested import fuzz, success_map, crash_map

fuzz(harness, keep_testing=True) # keep testing allows us to collect "all" crashes
%xmode plain

from battle_tested import fuzz, success_map, crash_map

fuzz(harness, keep_testing=True) # keep testing allows us to collect "all" crashes
import sys
sys.stderr.write = lambda i:i

from battle_tested import fuzz, success_map, crash_map

fuzz(harness, keep_testing=True) # keep testing allows us to collect "all" crashes
len(success_map())
from sqlitedict import SqliteDict

def harness(key, value):
    """ this tests what can be assigned in SqliteDict's keys and values """
    mydict = SqliteDict(":memory:", autocommit=True)
    mydict[key] = value
fuzz(harness, keep_testing=True) # keep testing allows us to collect "all" crashes
len(success_map())
crash_map()
import sqlitedict
sqlitedict.__getattribute__('__setitem__')
sqlitedict.SqliteDict.__getattribute__('__setitem__')
sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),'__setitem__')
s=SqlitDict(':memory:')
s=SqliteDict(':memory:')
dir(s)
sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),'__setitem__')
type(sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),'__setitem__'))
type(sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),'__setitem__')).__name__
[sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),i) for i in dir(s)]
[sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),i) for i in dir(s) if type(sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),i)).__name__=='method']




class_methods = [sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),i) for i in dir(s) if type(sqlitedict.SqliteDict.__getattribute__(SqliteDict(':memory:'),i)).__name__=='method']

for i in class_methods:
    name = i.__name__
    fuzz(i, keep_testing=True)
    c_map = crash_map()
    print(name, c_map)
