# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2019-04-30 07:20:45
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2019-04-30 07:44:37

from typing import Callable
from re import findall
from functools import lru_cache

@lru_cache(64) # this can be an expensive operation, so use caching
def function_arg_count(fn:Callable) -> int:
    """ finds how many args a function has """
    assert callable(fn), 'function_arg_count needed a callable function, not {0}'.format(repr(fn))
    # normal functions
    if (    hasattr(fn, '__code__')
            and hasattr(fn.__code__, 'co_argcount')
            and isinstance(fn.__code__.co_argcount, int)
            and fn.__code__.co_argcount >= 0):
        return fn.__code__.co_argcount
    # partials
    elif (  hasattr(fn, 'args')
            and hasattr(fn.args, '__len__')
            and hasattr(fn, 'func')
            and callable(fn.func)
            and hasattr(fn, 'keywords')
            and hasattr(fn.keywords, '__len__')):
        # partials
        return function_arg_count(fn.func) - (len(fn.args) + len(fn.keywords))
    # brute force
    else:
        # attempts to brute force and find how many args work for the function
        number_of_args_that_work = []
        for i in range(1, 64):
            try:
                fn(*range(i))
            except TypeError as ex:
                search = findall(r'((takes (exactly )?(one|[0-9]{1,}))|(missing (one|[0-9]{1,})))', repr(ex))
                our_specific_type_error = len(repr(findall(r'((takes (exactly )?(one|[0-9]{1,}))|(missing (one|[0-9]{1,})))', repr(ex))))>10
                if not our_specific_type_error: # if you find something
                    number_of_args_that_work.append(i)
                pass
            except Exception:
                #number_of_args_that_work.append(i)
                pass
            else:
                number_of_args_that_work.append(i)
        # if brute forcing worked, return the smallest count that did
        if len(number_of_args_that_work):
            return min(number_of_args_that_work)
        #logging.warning('using backup plan')
        return 1 # not universal, but for now, enough... :/


if __name__ == '__main__':
    from functools import partial

    # ensure it works with its basic functionality
    def test_0():
        pass
    assert function_arg_count(test_0) == 0
    def test_1(a):
        pass
    assert function_arg_count(test_1) == 1
    def test_2(a, b):
        pass
    assert function_arg_count(test_2) == 2

    # ensure it works with lambdas
    assert function_arg_count(lambda: None) == 0
    assert function_arg_count(lambda a: None) == 1
    assert function_arg_count(lambda a,b: None) == 2
    assert function_arg_count(lambda a,b,c: None) == 3
    assert function_arg_count(lambda a,b,c,d: None) == 4

    # ensure it works on itself
    assert function_arg_count(function_arg_count) == 1

    # function_arg_count returns how many args are left to fuzz. partials imply
    # that one of the args needs to be locked down to a specific value
    assert function_arg_count(partial(test_2, 'pancakes')) == 1
    assert function_arg_count(partial(
        lambda a, b: None,
        'waffles'
    )) == 1
