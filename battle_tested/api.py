# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2019-04-28 10:43:15
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2019-04-30 08:47:31

from typing import Callable
from strict_functions import overload
from function_arg_count import function_arg_count

fn, seconds=6, max_tests=1000000000, verbose=False, keep_testing=True, quiet=False, allow=(), strategy=garbage

class default:
    ''' this namespace is where all of BT's default settings go '''
    max_tests = 1000000000      # by default stop at one billion tests
    seconds = 6                 # by default fuzz the function for 6 seconds
    input_types = tuple()       # by default use ALL of its available input types
    exit_on_first_crash = False # by default collect the exceptions, dont raise them
    allow = tuple()             # by default track ALL exception types
    verbosity = 1               # by default show the fuzz result being produced

class verify:
    """collection of validation functions for the api"""
    @staticmethod
    def seconds(_seconds):
        assert type(_seconds) == int, 'battle_tested needs seconds to be an int, not {0}'.format(repr(_seconds))
        assert _seconds > 0, 'battle_tested needs seconds to be a positive int, not {0}'.format(repr(_seconds))

    @staticmethod
    def verbosity(_verbosity):
        """ asserts that verbosity setting is valid """
        assert type(_verbosity) == int, 'battle_tested needs verbosity to be a int, not {}'.format(repr(_verbosity))
        # do not reformat the following assertion
        assert _verbosity in {
            0: "quiet", 1: "normal", 2: "extreme"
        }, 'battle_tested needs verbosity to be 0, 1, or 2. - {}'.format(_verbosity)

    @staticmethod
    def max_tests(_max_tests):
        """ asserts that max_tests is valid """
        assert type(_max_tests) == int, 'battle_tested needs max_tests to be an int, not {0}'.format(repr(_max_tests))
        assert _max_tests > 0, 'battle_tested needs max_tests to be a positive int, not {0}'.format(repr(_max_tests))

    @staticmethod
    def function(fn):
        """ asserts that the input is a function """
        if not callable(fn):
            raise TypeError('battle_tested needs a callable function, not {0}'.format(repr(fn)))
        args = function_arg_count(fn)
        if not isinstance(args, int):
            raise TypeError('expected an int, not {0}'.format(args))
        if args <= 0:
            raise ValueError('battle_tested cannot fuzz a function that accepts "{0}" args'.format(args))

    @staticmethod
    def exit_on_first_crash(_exit_on_first_crash):
        """ ensures exit_on_first_crash is a valid argument """
        assert type(_exit_on_first_crash) == bool, 'exit_on_first_crash needs to be a bool, not {0}'.format(repr(_exit_on_first_crash))
        assert _exit_on_first_crash in {True, False}, 'invalid value for exit_on_first_crash: {0}'.format(repr(_exit_on_first_crash))

    @staticmethod
    def allow(_allow):
        """ ensures allow is a valid argument """
        assert type(_allow) == tuple, 'battle_tested needs allow to be a tuple, not {0}'.format(repr(_allow))
        for ex in _allow:
            assert issubclass(ex, BaseException), 'allow only accepts exceptions as its members, found: {0}'.format(ex)

    @staticmethod
    def fuzz_arguments(args: Dict):
        assert isinstance(args, dict), args
        assert args, args
        for required in ["max_tests", "seconds", "input_types", "exit_on_first_crash", "allow", "verbosity"]:
            assert required in args, 'missing argument: "{}" in {}'.format(required, args)
            assert hasattr(verify, required), 'missing verification function "{}"'.format(required)
            verification_function = getattr(verify, required)
            assert callable(verification_function), verification_function
            verification_function(args[required])



# this is the primary usage and supports both "fuzz(fn)" and "@fuzz" syntaxes
def fuzz(   fn: Callable,
            *, # force settings to be kv pairs
            max_tests=default.max_tests,
            seconds=default.seconds,
            input_types=default.input_types,
            exit_on_first_crash=default.exit_on_first_crash,
            allow=default.allow,
            verbosity=default.verbosity):
    verify.fuzz_arguments(locals())

# this is for the "@fuzz()" decorator syntax, to allow users to input settings
@overload
def fuzz(   *, # force settings to be kv pairs
            max_tests=default.max_tests,
            seconds=default.seconds,
            input_types=default.input_types,
            exit_on_first_crash=default.exit_on_first_crash,
            allow=default.allow,
            verbosity=default.verbosity):
    return partial(fuzz, **locals())
