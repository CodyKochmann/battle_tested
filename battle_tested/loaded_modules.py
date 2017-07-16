# -*- coding: utf-8 -*-
# @Author: cody
# @Date:   2017-06-27 14:18:29
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-07-06 13:50:32

import sys
from inspect import currentframe

import itertools
import requests
import numpy
import scipy
import django
import logging
import os
import hypothesis
import functools

def is_module(module, mod_type=type(sys)):
    """ returns true if the input is a module """
    return type(module) == mod_type

def is_type(t):
    """ returns true if input is a constructible type """
    return isinstance(t, type) and \
        hasattr(t, '__init__') and \
        callable(t.__init__) and \
        (not isinstance(t, BaseException)) and \
        (not repr(t).split("'")[0].startswith('_'))

def module_types(module):
    """ returns all types from the given module """
    #assert is_module(module), 'needed module, got {}'.format(type(module))
    if is_module(module) and hasattr(module, '__dict__'):
        d = module.__dict__
        types = (d[i] if is_type(d[i]) else type(d[i]) for i in d if type(d[i])!=None)
        #types = (i for i in types if not i.__name__.startswith('builtin'))
        types = (i for i in types if hasattr(i, '__init__'))
        return set(types)
    else:
        return set()

def nested_modules(module):
    """ returns a set of nested modules from the given module """
    if is_module(module) and hasattr(module, '__dict__'):
        d = module.__dict__
        return set(d[i] for i in d if type(d[i]).__name__ == 'module')
    else:
        return set()

class collection():
    modules = set() # where collected modules are stored
    modules.add(sys.modules['__main__']) # explicitly add __main__ module
    types = set() # where collected types are stored

    # any types with a lowercased __repr__ containing any of these are taken out
    # of the collected types due to the danger in fuzzing their constructors.
    blacklist_terms = 'sre.', 'inspect', 'abc', 'os.', 'sys.', 'io.', 'weak'
    blacklist_terms+= 'thread', 'process', 'frozen', 'import', 'eval', 'exec'
    blacklist_terms+= 'exit', 'error', 'excep', 'ctype', 'buffer', 'operator',
    blacklist_terms+= 'caller', 'pickle', 'file', 'warning', 'pipe', 'socket'
    blacklist_terms+= 'code', 'fail', 'battle_tested', 'handle', 'event', 'ast.'

    def injest(arg,types=types,modules=modules,blacklist_terms=blacklist_terms):
        """ injests modules and types and stores them """
        try:
            #print(arg)
            if is_module(arg):
                modules.add(arg)
            elif is_type(arg):
                    types.add(arg)
            else:
                if is_type(type(arg)):
                    types.add(type(arg))
        except:
            pass
    # add the top level modules from the frame and sys.modules
    for i in (sys.modules, currentframe().f_globals, currentframe().f_locals):
        map(injest, i.values())
    # _previous_len = 0
    # while _previous_len!=len(modules):
    #     _previous_len = len(modules)
    for i in range(1):
        for m in modules:
            map(injest, m.__dict__.values())

    generated_functions = set()

blacklisted = lambda t:any(i in repr(t).lower() for i in collection.blacklist_terms)
print('before',len(collection.types))
collection.types = set(i for i in collection.types if not blacklisted(i))
print('after',len(collection.types))

for i in collection.types:
    print(i)
'''
out = set()
for i in collection.modules:
    for x in i.__dict__.values():
        if isinstance(type(x), type) and 'built-in' not in repr(x):
            if type(x) == type:
                out.add(x)
            else:
                out.add(type(x))
out = sorted(out)
for i in out:
    print(i)
'''
# for i in collection.types:
#     print(i)
print(len(collection.types))
exit()





previous_len=-1
while len(collection.modules) != previous_len:
    previous_len = len(collection.modules)
    for t in list(collection.modules):
        {collection.modules.add(m) for m in nested_modules(t)}
        {collection.types.add(m) for m in module_types(t)}
    collection.modules = collection.modules

collection.types = (i for i in collection.types if not any(b in repr(i) for b in ('os.', 'sys.', 'abc.', 'thread','process', '_frozen_importlib_external', '_frozen_importlib')))
collection.types = set(i for i in collection.types if hasattr(i,'__init__'))


def find_working_args(fn):
    ''' returns how many arguments work with the function '''
    from battle_tested import garbage
    working_args = set()
    for i in range(8):
        for attempt in range(8):
            if i in working_args or (i>3 and len(working_args)/i<0.5):
                break
            try:
                    fn(*(garbage.example() for arg in range(i)))
                    working_args.add(i)
                    yield i
            except:
                pass




from boltons.funcutils import FunctionBuilder

def build_test_function(fn, args=0):
    ''' returns a test function with the given number of arguments '''

    name='{}_{}_tester_{}'.format(fn.__module__,fn.__name__,args)
    function_body='import {};from battle_tested import garbage;return {}.{}({})'.format(
        fn.__module__,
        fn.__module__,
        fn.__name__,
        ', '.join('garbage.example()' for i in range(args))
    )
    return FunctionBuilder(
        name=name,
        body=function_body,
        ).get_func()

g = (repr(i) for i in collection.types)
for t in sorted(g):
    print(t)


"""
exit('the code below is dangerous')

for t in collection.types:
    for wa in find_working_args(t):
        print(t,wa)
        collection.generated_functions.add(build_test_function(t,wa))


for t in collection.types:
    print("{:30}{:30}{}".format(t.__module__,t.__name__,t.__init__))
print(collection.modules)
print('---------------')
print(collection.types)

print('---------------')
print(len(collection.modules),'modules')
print(len(collection.types),'types')
'''
for f in collection.generated_functions:
    #print(f,f.__code__.co_argcount)
    out = 'undefinednone'
    for i in range(32):
        try:
            out = f()
            print(f,out)
            break
        except:
            pass
    if out == 'undefinednone':
        print(f,'didnt work----------------------------------')

'''

for i in range(4):
    print('-'*40)

"""


''' holy shit the stuff below is dangerous '''

"""
def violent_furniture_generator():
    while 1:
        for f in collection.generated_functions:
            try:
                out = f()
                yield out
            except:
                pass
violent_furniture = violent_furniture_generator()
next(violent_furniture)
generate_furniture = lambda i:(violent_furniture.send(None),)

from hypothesis import strategies as st

furniture = st.none().map(generate_furniture)

for i in range(8):
    print(furniture.example())
"""
