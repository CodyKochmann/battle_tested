# -*- coding: utf-8 -*-
# @Author: cody
# @Date:   2017-06-27 14:18:29
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-07-06 13:50:32

import sys
from inspect import currentframe

import ipaddress

from battle_tested import garbage, battle_tested


@battle_tested(max_tests=50)
def is_module(module, mod_type=type(sys)):
    """ returns true if the input is a module """
    return type(module) == mod_type

@battle_tested(max_tests=50)
def is_type(t):
    """ returns true if input is a constructible type """
    return isinstance(t, type) and \
        hasattr(t, '__init__') and \
        callable(t.__init__) and \
        (not isinstance(t, BaseException)) and \
        (not repr(t).split("'")[0].startswith('_'))

@battle_tested(max_tests=50)
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

@battle_tested(max_tests=50)
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
    variables = set() # where collected variables are stored

    # any types with a lowercased __repr__ containing any of these are taken out
    # of the collected types due to the danger in fuzzing their constructors.
    blacklist_terms = 'sre.', 'inspect', 'abc', 'os.', 'sys.', 'io.', 'weak'
    blacklist_terms+= 'thread', 'process', 'frozen', 'import', 'eval', 'exec'
    blacklist_terms+= 'exit', 'error', 'excep', 'ctype', 'buffer', 'operator',
    blacklist_terms+= 'caller', 'pickle', 'file', 'warning', 'pipe', 'socket'
    blacklist_terms+= 'code', 'fail', 'battle_tested', 'handle', 'event', 'ast.'

    def injest(arg,types=types,modules=modules,blacklist_terms=blacklist_terms,variables=variables):
        """ injests modules and types and stores them """
        try:
            variables.add(arg)
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

@battle_tested(max_tests=50)
def blacklisted(t):
    return any((i in repr(t).lower()) for i in collection.blacklist_terms)


#print('before',len(collection.types))
collection.types = set(i for i in collection.types if not blacklisted(i))
#print('after',len(collection.types))

print(len(collection.variables))

@battle_tested(max_tests=50)
def find_working_args(fn, garbage=garbage):
    ''' returns how many arguments work with the function '''
    if callable(fn):
        working_args = set()
        for i in range(6):
            for attempt in range(20):
                if i in working_args: # or (i>3 and len(working_args)/i<0.5):
                    pass
                else:
                    try:
                        out = None
                        out=fn(*(garbage.example() for arg in range(i)))
                        if out != None:
                            working_args.add(i)
                            yield i
                    except Exception as e:
                        pass

from boltons.funcutils import FunctionBuilder
from re import findall
@battle_tested()
def legal_fn_name_chars(i):
    ''' returns the letters and underscores found in the input '''
    if type(i)==str:
        return '_'.join(findall(r'[a-zA-Z\_]{1,}', i))
    else:
        return ''
exit()



def build_test_function(fn, args=0):
    ''' returns a test function with the given number of arguments '''
    name='{}_{}_tester'.format(
        legal_fn_name_chars(fn.__module__),
        legal_fn_name_chars(fn.__name__),
        args
    )
    #print('building:',name)
    from battle_tested import garbage
    function_body='import {};from battle_tested import garbage;return {}.{}({})'.format(
        fn.__module__,
        fn.__module__,
        fn.__name__,
        ', '.join('garbage.example()' for i in range(args))
    )
    function_body='out=t({});return (None if isinstance(out, BaseException) else out)'.format(
        ', '.join('garbage.example()' for i in range(args))
    )
    return FunctionBuilder(
        name=name,
        body=function_body,
        args=('n', 't', 'garbage') , # n is there for hypothesis.strategies.none input
        defaults=(None, fn, garbage),
        ).get_func()

g = (repr(i) for i in collection.types)
for t in sorted(g):
    print(t)

for t in collection.types:
    t=t if type(t) == type else type(t)
    #print('trying:',t)
    for wa in find_working_args(t):
        f = build_test_function(t,wa)
        collection.generated_functions.add(f)
        print('total built:',len(collection.generated_functions),'type:',t,'args:',wa)

print('total built:',len(collection.generated_functions))

def violent_furniture_generator():
    while 1:
        for f in collection.generated_functions:
            try:
                out = f()
                yield out
            except BaseException as ex:
                if type(ex) in (KeyboardInterrupt,GeneratorExit):
                    raise ex
                pass

violent_furniture = violent_furniture_generator()
next(violent_furniture)

def generate_furniture(n=None, violent_furniture=violent_furniture):
    while 1:
        #print('trying')
        try:
            out = violent_furniture.send(None)
            return out
        except BaseException as ex:
            if type(ex) == KeyboardInterrupt:
                raise ex
            pass



from hypothesis import strategies as st

furniture = st.none().map(generate_furniture)

print('trying violent_furniture now...')

for i in range(1024):
    out = generate_furniture()
    try:
        print(out)
    except:
        pass


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
