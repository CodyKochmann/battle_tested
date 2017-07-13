from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
import re
# the target function
import os
from os import scandir as ls
def walk(dir='./'):
  '''hello'''
  print('running walk')
  scan_queue=[ls(dir)]
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

def leading_spaces(line):
    return ''.join(takewhile(lambda c:c==' ', iter(line.split('\n')[-1])))

def build_line_to_inject(previous_line):
    quotes_to_use='"""' if '"""' not in previous_line else "'''"
    return '{0}storage.frames.append(({2}{1}{2}, inspect.currentframe()))'.format(
        leading_spaces(previous_line),
        previous_line,
        quotes_to_use
    )

def inject_frames(fn):
    previous=''
    for i in function_lines(walk):
        if previous!=None:
            quotes_to_use='"""' if '"""' not in previous else "'''"
            yield '{0}storage.frames.append({2}{1}{2}, inspect.currentframe())'.format(
                leading_spaces(i),
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

def cmp(src):
    return compile(src, 'tmp', 'exec')
def try_code(src):
    try:
        cmp(src)
        return True
    except Exception:
        return False

def connected_lines(fn):
    ''' returns the lines in a function that need to be connected '''
    previous = ''
    out=''
    old_dis=dis_calls(out)
    for line in getsource(fn).splitlines():
        out+=line
        if try_code(out) and len(line.strip()) and not line.strip()[0] in '\'"#':
            yield out.replace(previous, '')
            previous = out
            old_dis=dis_calls(out)
        out+='\n'

from boltons.funcutils import FunctionBuilder

def build_function(name, body):
    return FunctionBuilder(name, doc='', body=body).get_func()

collected_code = []

for i in connected_lines(walk):
    collected_code.append(i)
    to_be_injected = build_line_to_inject(i)
    if try_code('\n'.join(collected_code+[to_be_injected])) and not i.strip().startswith('return'):
        collected_code.append(to_be_injected)
    print(len(collected_code), try_code('\n'.join(collected_code)))
    bar()
    print('\n'.join(collected_code))
    bar()

bar()

exec(cmp('\n'.join(collected_code)))
print(len(storage.frames))
walk()
print(len(storage.frames))
bar()
print('removing duplicate frames')
# remove frames entered for the same line
final_frames = {}
for i in storage.frames:
    final_frames[i[0]] = i[1]

bar()

def frame_variables(frame):
    ' takes a frame and returns what variables were available at that location '
    out = {}
    #out.update(frame.f_builtins)
    out.update(frame.f_globals)
    out.update(frame.f_locals)
    return out

bar()
bar()
bar()

def remove_comments(code):
    out = []
    incomment = False
    for line in code.split('\n'):
        out.append(''.join(takewhile(lambda c:c!='#',iter(line))))
    return '\n'.join(out)

from pprint import pprint

for line in final_frames:
    frame = final_frames[line]
    line = remove_comments(line)
    frame_vars = frame_variables(frame)

    relative_vars = [k for k in frame_vars if k in re.findall(r'[a-zA-Z_]{1,}', line)]
    print(line)
    bar()
    line_vars = {k:frame_vars[k] for k in relative_vars}
    try:
        pprint(line_vars)
    except:
        print(line_vars)
    bar()
    bar()

"""
frame = storage.frames[0][1]

for i in dir(frame):
    if i.startswith('f_'):
        print(i, getattr(frame, i))
        bar()"""
'''
the important ones are co_names and co_varnames
from fn.__code__
'''

bar()
#print(frame_variables(frame))

print(getsource(walk))
