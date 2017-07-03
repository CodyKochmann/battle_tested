# -*- coding: utf-8 -*-
# @Author: cody
# @Date:   2017-06-27 14:18:29
# @Last Modified by:   cody
# @Last Modified time: 2017-06-27 16:02:36

import sys

def is_module(module):
    return type(module).__name__ == 'module', 'needed module, got {}'.format(type(module))

def module_types(module):
    """ returns all types from the given module """
    assert is_module(module)
    d = module.__dict__
    types = (type(d[i]) for i in d)
    types = (i for i in types if not i.__name__.startswith('builtin'))
    types = (i for i in types if '__init__' in dir(i))
    return set(types)

def nested_modules(module):
    """ returns a set of nested modules from the given module """
    assert is_module(module)
    d = module.__dict__
    return set(d[i] for i in d if type(d[i]).__name__ == 'module')

target_modules = set(sys.modules.values())

class collection():
    modules = set()
    types = set()

previous_len=0
current=1
iterations=0
while current != previous_len:
    iterations+=1
    previous_len = len(target_modules)
    for t in list(target_modules):
        {collection.modules.add(m) for m in nested_modules(t)}
        {collection.types.add(m) for m in module_types(t)}
    target_modules = collection.modules
    current = len(target_modules)

print(collection.modules)
print('---------------')
print(collection.types)

print('---------------')
print(iterations)
print(len(collection.modules),'modules')
print(len(collection.types),'types')

