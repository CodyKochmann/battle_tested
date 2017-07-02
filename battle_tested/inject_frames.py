from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals

# the target function
def walk(dir='./'):
  scan_queue=[ls(dir)]
  '''hello'''
  out=[]
  while len(scan_queue):
    # pop the next item to scan
    for i in scan_queue.pop():
      # yield its path
      out.append(i.path)
      # if directory, add it to the queue
      if i.is_dir():
        scan_queue.append(ls(i.path))
  return out

def bar():
    print('-'*20)
#============================================
from dis_list import dis_calls, dis_list
import inspect
from inspect import getsource, currentframe

class storage():
    frames=[]
    yielded=[]
    
def gen_frame_line(l):
    ''' generates the frame builder for the given line of source '''

def line_keywords(l):
    pass


for a in dir(inspect):
    if type(getattr(inspect,a)).__name__=='function':
        try:
            print(a,'\n',getattr(inspect,a)(walk))
            bar()
        except :
            pass
bar()
bar()
for i in dir(walk.__code__):
    a=getattr(walk.__code__,i)
    if i.startswith('co_'):
        print(i,'\n',a)
        bar()





def function_lines(fn):
    for i in getsource(fn).splitlines():
        yield i

og_dis=dis_calls(walk)
#print(og_dis)

print('+'*20)
from itertools import takewhile



def inject_frames(fn):
    previous=''
    for i in function_lines(walk):
        if previous!=None:
            leading_spaces=takewhile(lambda c:c==' ', iter(i))
            leading_spaces=''.join(leading_spaces)
            quotes_to_use='"""' if '"""' not in previous else "'''"
            yield '{0}storage.frames.append({2}{1}{2}, inspect.currentframe())'.format(
                leading_spaces,
                previous,
                quotes_to_use
                )
        if not (i.strip().endswith(':') or i.strip()[0] in '\'"#' or len(i.strip())==0):
            compile('\n'.join(storage.yielded), 'sumstring', 'exec')
        previous=i
        yield i
    
for i in inject_frames(walk):
    print(i)

bar()
bar()

#import pdb;pdb.set_trace()
bar()
bar()

def connected_lines(fn):
    ''' returns the lines in a function that need to be connected '''
    def cmp(src):
        return compile(src, 'tmp', 'exec')
    def try_code(src):
        try:
            cmp(src)
            return True
        except Exception:
            return False
    out=''
    old_dis=dis_calls(out)
    for line in getsource(fn).splitlines():
        out+=line
        if try_code(out) and len(line.strip()) and not line.strip()[0] in '\'"#':
            yield out
            old_dis=dis_calls(out)
        out+='\n'

for i in connected_lines(walk):
    print(i)
    bar()

'''
the important ones are co_names and co_varnames
from fn.__code__
'''

