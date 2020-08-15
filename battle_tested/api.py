# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2019-04-28 10:43:15
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2019-04-30 08:47:31

from typing import Callable
from functools import partial
from function_arg_count import function_arg_count
from FuzzResult import FuzzResult
from runner import run_fuzz

# how the previous api worked
#
#   fn, seconds=6, max_tests=1000000000, verbose=False, keep_testing=True, quiet=False, allow=(), strategy=garbage
#

def _verify_function(fn):
    """ asserts that the input is a function """
    if not callable(fn):
        raise TypeError('battle_tested needs a callable function, not {0}'.format(repr(fn)))
    args = function_arg_count(fn)
    if not isinstance(args, int):
        raise TypeError('expected an int, not {0}'.format(args))
    if args <= 0:
        raise ValueError('battle_tested cannot fuzz a function that accepts "{0}" args'.format(args))

def _verify_max_tests(_max_tests):
    """ asserts that max_tests is valid """
    assert type(_max_tests) == int, 'battle_tested needs max_tests to be an int, not {0}'.format(repr(_max_tests))
    assert _max_tests > 0, 'battle_tested needs max_tests to be a positive int, not {0}'.format(repr(_max_tests))


def _verify_seconds(_seconds):
    assert type(_seconds) == int, 'battle_tested needs seconds to be an int, not {0}'.format(repr(_seconds))
    assert _seconds > 0, 'battle_tested needs seconds to be a positive int, not {0}'.format(repr(_seconds))


def _is_tuple_of_types(types):
    assert isinstance(types, tuple), types
    return all(isinstance(i, type) for i in types)

def _is_type_or_tuple_of_types(t):
    assert isinstance(t, (tuple, type))
    return isinstance(t, type) or _is_tuple_of_types(t)

def _is_nested_tuple_of_types(types):
    assert isinstance(types, tuple), types
    return all(_is_type_or_tuple_of_types(i) for i in types)

def _verify_input_types(_input_types):
    assert type(_input_types) == tuple, 'battle_tested needs seconds to be an tuple, not {0}'.format(repr(_input_types))
    assert _is_tuple_of_types(_input_types
        ) or _is_nested_tuple_of_types(_input_types
        ), 'battle_tested needs input_types to be a tuple of types or a tuple multiple types, not {0}'.format(repr(_input_types))


def _verify_exit_on_first_crash(_exit_on_first_crash):
    """ ensures exit_on_first_crash is a valid argument """
    assert type(_exit_on_first_crash) == bool, 'exit_on_first_crash needs to be a bool, not {0}'.format(repr(_exit_on_first_crash))
    assert _exit_on_first_crash in {True, False}, 'invalid value for exit_on_first_crash: {0}'.format(repr(_exit_on_first_crash))


def _verify_allow(_allow):
    """ ensures allow is a valid argument """
    assert type(_allow) == tuple, 'battle_tested needs allow to be a tuple, not {0}'.format(repr(_allow))
    for ex in _allow:
        assert issubclass(ex, BaseException), 'allow only accepts exceptions as its members, found: {0}'.format(ex)


def _verify_verbosity(_verbosity):
    """ asserts that verbosity setting is valid """
    assert type(_verbosity) == int, 'battle_tested needs verbosity to be a int, not {}'.format(repr(_verbosity))
    # do not reformat the following assertion
    assert _verbosity in {
        0: "quiet", 1: "normal", 2: "extreme"
    }, 'battle_tested needs verbosity to be 0, 1, or 2. - {}'.format(_verbosity)


def _verify_input_types_fits_function(fn, input_types):
    _verify_function(fn)
    _verify_input_types(input_types)
    assert len(input_types) == function_arg_count(fn), 'battle_tested needs input_types to be the same length as the arg count of {}, found {} not {}'.format(fn, len(input_types), function_arg_count(fn))


def _verify_fuzz_settings(*, fn=None, max_tests=None, seconds=None, input_types=None, exit_on_first_crash=None, allow=None, verbosity=None):
    _verify_function(fn)
    _verify_max_tests(max_tests)
    _verify_seconds(seconds)
    _verify_input_types(input_types)
    _verify_exit_on_first_crash(exit_on_first_crash)
    _verify_allow(allow)
    _verify_verbosity(verbosity)
    if len(input_types):
        _verify_input_types_fits_function(fn, input_types)


# this is the primary usage and supports "fuzz(fn)" syntax
def _fuzz_decorator(
            fn: Callable,
            *, # force settings to be kv pairs
            max_tests=1000000000,
            seconds=6,
            input_types=tuple(),
            exit_on_first_crash=False,
            allow=tuple(),
            verbosity=1):
    _verify_fuzz_settings(**locals())

    # placeholder for now. decorators basically queue a fuzz for multiprocessing madness
    #return QueuedFuzzResult(locals())

    return fn


def _fuzz_function(
            fn: Callable,
            *, # force settings to be kv pairs
            max_tests=1000000000,
            seconds=6,
            input_types=tuple(),
            exit_on_first_crash=False,
            allow=tuple(),
            verbosity=1):

    _verify_fuzz_settings(**locals())

    return FuzzResult(run_fuzz(**locals()))


# this is for the "@fuzz()" decorator syntax, to allow users to input settings
def fuzz(   fn=None,
            *, # force settings to be kv pairs
            max_tests=100_000,
            seconds=6,
            input_types=tuple(),
            exit_on_first_crash=False,
            allow=tuple(),
            verbosity=1):

    if fn is None:
        return partial(_fuzz_decorator, **{k:v for k,v in locals().items() if k != 'fn'})
    else:
        return _fuzz_function(**locals())


if __name__ == '__main__':

    def my_adder(a, b):
        return a + b

    # uncomment to get right to debugging
    #result = fuzz(my_adder, verbosity=2)

    # test multiple runs
    result = fuzz(my_adder)
    print(result)
    assert isinstance(result, FuzzResult)

    result = fuzz(my_adder)
    print(result)
    assert isinstance(result, FuzzResult)

    result = fuzz(my_adder)
    print(result)
    assert isinstance(result, FuzzResult)


    # test various settings
    # test seconds
    # not implemented yet
    #result = fuzz(my_adder, seconds=3)
    #print(result)
    #assert isinstance(result, FuzzResult)

    result = fuzz(my_adder, input_types=(int, str))
    print(result)
    assert isinstance(result, FuzzResult)

    result = fuzz(my_adder, input_types=((int, str), (bool, bool)))
    print(result)
    assert isinstance(result, FuzzResult)

    result = fuzz(my_adder, input_types=(int, (list, float, bool)))
    print(result)
    assert isinstance(result, FuzzResult)

    # not implemented yet
    #result = fuzz(my_adder, exit_on_first_crash=True)
    #print(result)
    #assert isinstance(result, FuzzResult)

    #result = fuzz(my_adder, allow=(AssertionError,))
    #print(result)
    #assert isinstance(result, FuzzResult)

    # only uncomment if you wanna REALLY see some logs
    #result = fuzz(my_adder, verbosity=2)
    #print(result)
    #assert isinstance(result, FuzzResult)


    # test decorator syntax
    @fuzz(seconds=3)
    def my_adder_1(a, b):
        return a + b
    assert callable(my_adder_1)
    assert my_adder_1.__name__ == 'my_adder_1'

    @fuzz(input_types=(int, str))
    def my_adder_2(a, b):
        return a + b
    assert callable(my_adder_2)
    assert my_adder_2.__name__ == 'my_adder_2'

    @fuzz(input_types=((int, str), (bool, bool)))
    def my_adder_3(a, b):
        return a + b
    assert callable(my_adder_3)
    assert my_adder_3.__name__ == 'my_adder_3'

    @fuzz(input_types=(int, (list, float, bool)))
    def my_adder_4(a, b):
        return a + b
    assert callable(my_adder_4)
    assert my_adder_4.__name__ == 'my_adder_4'

    @fuzz(exit_on_first_crash=True)
    def my_adder_5(a, b):
        return a + b
    assert callable(my_adder_5)
    assert my_adder_5.__name__ == 'my_adder_5'

    @fuzz(allow=(AssertionError,))
    def my_adder_6(a, b):
        return a + b
    assert callable(my_adder_6)
    assert my_adder_6.__name__ == 'my_adder_6'

    @fuzz(verbosity=2)
    def my_adder_7(a, b):
        return a + b
    assert callable(my_adder_7)
    assert my_adder_7.__name__ == 'my_adder_7'


    print('success')
