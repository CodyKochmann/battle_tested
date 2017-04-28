# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-04-26 11:41:19
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-04-28 13:55:07

from __future__ import print_function
from functools import wraps
import logging
import better_exceptions
from hypothesis import given, strategies as st, settings, Verbosity
from gc import collect as gc


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


from time import time

class generators(object):
    def started(generator_function):
        """ starts a generator when created """
        def wrapper(*args, **kwargs):
            g = generator_function(*args, **kwargs)
            next(g)
            return g
        return wrapper

    @staticmethod
    @started
    def sum():
        "generator that holds a sum"
        total = 0
        while 1:
            total += yield total

    @staticmethod
    @started
    def counter():
        "generator that holds a sum"
        c = 0
        while 1:
            yield c
            c += 1

    @staticmethod
    @started
    def avg():
        """ generator that holds a rolling average """
        count = 0.0
        total = generators.sum()
        i=0
        while 1:
            i = yield (total.send(i)*1.0/count if count else 0)
            count += 1

    @staticmethod
    @started
    def timer():
        """ generator that tracks time """
        start_time = time()
        previous = start_time
        while 1:
            yield time()-start_time


from threading import Timer

class IntervalTimer(object):
    """ run functions on intervals in the background
        by: Cody Kochmann
    """
    def __init__(self, seconds, function):
        assert type(seconds) in (int,float)
        assert callable(function)
        self.seconds=seconds
        self.function=function
        self.stopped=False
        self.running=False

    def start(self):
        if not self.stopped:
            if not self.running:
                self.function()
                self.running=True
            self.thread=Timer(self.seconds,self.function)
            self.thread.start()
            self.restart_thread=Timer(self.seconds, self.start)
            self.restart_thread.start()

    def stop(self):
        try:
            self.stopped = True
            self.running = False
            self.thread.cancel()
            self.restart_thread.cancel()
        except AttributeError:
            pass


def function_arg_count(fn):
    """ generates a list of the given function's arguments """
    assert callable(fn), 'function_arg_count needed a callable function, not {0}'.format(repr(fn))
    return fn.__code__.co_argcount

class battle_tested(object):
    """

battle_tested - automated function fuzzer to easily test production code

Example Usage:

    from battle_tested import battle_tested

    def test_function(a,b,c):
        return c,b,a

    battle_tested(test_function)

Or:

    from battle_tested import battle_tested

    @battle_tested()
    def test_function(a,b,c):
        return c,b,a

"""


    def __init__(self, seconds=2, max_tests=1000000, verbose=False, **kwargs):
        """ your general constructor to get things in line """

        # this is here if someone decides to use it as battle_tested(function)
        if callable(seconds):
            raise Exception('\n\n\tyou gave battle_tested() a function as the argument, did you mean battle_tested.fuzz()?')

        self.kwargs = kwargs
        self.tested = False

        # needed to determine how verbosly it will work
        self.__verify_verbose__(verbose)
        self.verbose = verbose
        # needed to determine the maximum time the tests can run
        self.__verify_seconds__(seconds)
        self.seconds = seconds
        # needed to determine maximum number of tests it can
        self.__verify_max_tests__(max_tests)
        self.max_tests = max_tests

    @staticmethod
    def __verify_seconds__(seconds):
        assert type(seconds) == int, 'battle_tested needs seconds to be an int, not {0}'.format(repr(seconds))
        assert seconds > 0, 'battle_tested needs seconds to be a positive int, not {0}'.format(repr(seconds))

    @staticmethod
    def __verify_verbose__(verbose):
        """ asserts that verbose is valid """
        assert type(verbose) == bool, 'battle_tested needs verbose to be a bool, not {0}'.format(repr(verbose))

    @staticmethod
    def __verify_max_tests__(max_tests):
        """ asserts that max_tests is valid """
        assert type(max_tests) == int, 'battle_tested needs max_tests to be an int, not {0}'.format(repr(max_tests))
        assert max_tests > 0, 'battle_tested needs max_tests to be a positive int, not {0}'.format(repr(max_tests))

    @staticmethod
    def __verify_function__(fn):
        """ asserts that the input is a function """
        assert callable(fn), 'battle_tested needs a callable function, not {0}'.format(repr(fn))

    @staticmethod
    def fuzz(fn, seconds=2, max_tests=1000000, verbose=False):
        """ staticly tests input funcions """
        battle_tested.__verify_function__(fn)
        battle_tested.__verify_seconds__(seconds)
        battle_tested.__verify_verbose__(verbose)
        battle_tested.__verify_max_tests__(max_tests)

        args_needed=function_arg_count(fn)

        # generate a strategy that creates a list of garbage variables for each argument
        strategy = st.lists(elements=garbage, max_size=args_needed, min_size=args_needed)

        print('testing: {0}'.format(fn.__name__))

        count = generators.counter()
        total = generators.sum()
        average = generators.avg()
        timer = generators.timer()

        def print_stats(count, timer, average):
            per_second = count/timer
            print('tests: {:<12} speed: {}/sec  avg: {}'.format(int(count),int(per_second),int(average.send(per_second))))
        interval = IntervalTimer(0.25, lambda:print_stats(next(count),next(timer),average))
        Timer(0.1,lambda:interval.start()).start()

        gc_interval = IntervalTimer(3, gc)
        gc_interval.start()

        @settings(timeout=seconds, max_examples=max_tests, verbosity=(Verbosity.verbose if verbose else Verbosity.normal))
        @given(strategy)
        def fuzz(arg_list):
            # unpack the arguments
            next(count)
            fn(*arg_list)
        # run the test
        fuzz()
        interval.stop()
        gc_interval.stop()
        print('battle_tested: no falsifying examples found')

    def __call__(self, fn):
        """ runs before the decorated function is called """
        self.__verify_function__(fn)

        if not self.tested:
            # only test the first time this function is called
            if not ('skip_test' in self.kwargs and self.kwargs['skip_test']):
                # skip the test if it is explicitly turned off
                self.fuzz(fn, seconds=self.seconds, max_tests=self.max_tests, verbose=self.verbose)
            self.tested = True

        def wrapper(*args, **kwargs):
            try:
                out = fn(*args, **kwargs)
            except Exception as e:
                # log the error
                if 'logger' in self.kwargs:
                    assert callable(self.kwargs['logger']), "battle_tested.logger needs to be a callable log function, not: {0}".format(repr(self.kwargs['logger']))
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
    #======================================
    #  Examples using the wrapper syntax
    #======================================

    @battle_tested(default_output=[], seconds=1, max_tests=5)
    def sample(i):
        return []

    @battle_tested()
    def sample2(a,b,c,d=''):
        t = a, b, c, d

    # proof that they only get tested once
    print(sample(4))
    print(sample2(1,2,3,4))
    print(sample('i'))
    print(sample2('a','b',2,4))

    #======================================
    #  Examples using the function syntax
    #======================================

    def sample3(input_arg):
        return True

    battle_tested.fuzz(sample3)

    battle_tested.fuzz(sample3, seconds=10)

    print('finished running battle_tested.py')
