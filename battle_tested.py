# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-04-26 11:41:19
# @Last Modified by:   cody
# @Last Modified time: 2017-04-27 11:18:58

from functools import wraps
import logging
import better_exceptions
from hypothesis import given, strategies as st, settings, Verbosity

garbage = (
    st.binary(),
    st.booleans(),
    st.characters(),
    st.complex_numbers(),
    st.decimals(),
    st.floats(),
    st.fractions(),
    st.integers(),
    st.none(),
    st.random_module(),
    st.randoms(),
    st.text(),
    st.tuples(),
    st.uuids()
)
garbage+=(
    st.lists(elements=st.one_of(*garbage)),
    st.iterables(elements=st.one_of(*garbage))
)
garbage=st.one_of(*garbage)


def function_args(fn):
    """ generates a list of the given function's arguments
        by: Cody Kochmann """
    assert callable(fn), 'function_args needed a callable function, not {0}'.format(repr(fn))
    try: # python2 implementation
        from inspect import getargspec
        return getargspec(fn).args
    except: # python3 implementation
        from inspect import signature
        return signature(fn).parameters

class battle_tested(object):
    """ A decorator that puts functions through hell so in production your code
        will have already seen worse.

        by: Cody Kochmann
    """

    def __init__(self, timeout=1, max_examples=1000000, verbose=False, **kwargs):
        """ your general constructor to get things in line """
        self.kwargs = kwargs
        self.tested = False
        self.verbose = verbose
        self.verbosity = (Verbosity.verbose if verbose else Verbosity.normal)
        assert type(timeout) == int, 'battle_tested needs timeout to be an int, not {}'.format(repr(timeout))
        self.timeout = timeout
        assert type(max_examples) == int, 'battle_tested needs max_examples to be an int, not {}'.format(repr(max_examples))
        self.max_examples = max_examples

    @staticmethod
    def test(fn, seconds=2, max_tests=1000000, verbose=False):
        """ staticly tests input funcions """
        args_needed=len(function_args(fn))
        # generate a strategy that creates a list of garbage variables for each argument
        strategy = st.lists(elements=garbage, max_size=args_needed, min_size=args_needed)

        if verbose:
            print('testing: {0}'.format(fn.__name__))


        @settings(timeout=seconds, max_examples=max_tests, verbosity=(Verbosity.verbose if verbose else Verbosity.normal))
        @given(strategy)
        def test(arg_list):
            # unpack the arguments
            fn(*arg_list)
        # run the test
        test()

    def battle_test(self,fn):
        """ where the function is actually battle tested """

        self.test(fn, seconds=self.timeout, max_tests=self.max_examples, verbose=self.verbose)

    def __call__(self, fn):
        """ runs before the decorated function is called """
        assert callable(fn), "battle_tested needs a callable target to wrap"

        if not self.tested:
            # only test the first time this function is called
            if not ('skip_test' in self.kwargs and self.kwargs['skip_test']):
                # skip the test if it is explicitly turned off
                self.battle_test(fn)
            self.tested = True

        def wrapper(*args, **kwargs):
            try:
                out = fn(*args, **kwargs)
            except Exception as e:
                # log the error
                if 'logger' in self.kwargs:
                    assert callable(self.kwargs['logger']), "battle_tested.logger needs to be a callable log function, not: {}".format(repr(self.kwargs['logger']))
                    self.kwargs['logger'](e)
                else:
                    logging.exception(e)
                # only raise the error if there isnt a default_output
                if 'default_output' in self.kwargs:
                    out = self.kwargs['default_output']
                else:
                    raise e
            return out
        return wrapper

if __name__ == '__main__':
    @battle_tested(default_output=[])
    def sample(i):
        return []

    @battle_tested(default_output=[])
    def sample2(i):
        return []


    @battle_tested(default_output=[])
    def sample23(a,b):
        return []

    print sample(4)
    print sample2(4)
    print sample(4)
    print sample2(4)

    def sample4(input_arg):
        return True

    battle_tested.test(sample4, verbose=True)

    print('finished running battle_tested.py')
