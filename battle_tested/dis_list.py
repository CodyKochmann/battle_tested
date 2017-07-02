from dis import dis
from io import StringIO
import sys

def f(a,b):
    return b,a

def return_stdout(fn):
    _old = sys.stdout
    out = StringIO()
    sys.stdout=out
    fn()
    sys.stdout=_old
    return out.getvalue()

def dis_list(fn): # lolololololol
    return [i[10:] for i in return_stdout(lambda:dis(fn)).splitlines() if len(i)>10]

def dis_calls(fn):
    return [i.strip().split(' ')[1] for i in dis_list(fn)]

for i in dis_list(f):
    print(i)
    
for c in dis_calls(f):
    print(c)


