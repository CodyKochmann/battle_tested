# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-04-27 12:49:17
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-06-14 16:42:01

"""
battle_tested - automated function fuzzer based on hypothesis to easily test production code

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

from __future__ import print_function
from functools import wraps
import logging
#import better_exceptions
from hypothesis import given, strategies as st, settings, Verbosity
from gc import collect as gc
import traceback
import sys
from time import time

__all__ = 'battle_tested', 'fuzz', 'disable_traceback', 'enable_traceback', 'garbage'

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
    st.uuids(),
    st.dictionaries(keys=st.text(), values=st.text())
)
garbage+=(
    # iterables
    st.lists(elements=st.one_of(*garbage)),
    st.iterables(elements=st.one_of(*garbage)),
    st.dictionaries(keys=st.text(), values=st.one_of(*garbage))
)
garbage=st.one_of(*garbage)

def is_py3():
    return sys.version_info >= (3, 0)

class tb_controls():
    old_excepthook = sys.excepthook
    no_tracebacklimit_on_sys='tracebacklimit' not in dir(sys)
    old_tracebacklimit = (sys.tracebacklimit if 'tracebacklimit' in dir(sys) else None)
    traceback_disabled = False

    @staticmethod
    def disable_traceback():
        if is_py3():
            sys.tracebacklimit = None
        else:
            sys.excepthook = lambda t, v, n:tb_controls.old_excepthook(t, v, None)
        tb_controls.traceback_disabled = True

    @staticmethod
    def enable_traceback():
        if tb_controls.traceback_disabled:
            if is_py3():
                if tb_controls.no_tracebacklimit_on_sys:
                    del sys.tracebacklimit
                else:
                    sys.tracebacklimit = tb_controls.old_tracebacklimit
            else:
                sys.excepthook = tb_controls.old_excepthook
            tb_controls.traceback_disabled = False

def enable_traceback():
    """ disables tracebacks from being added to exception raises """
    tb_controls.enable_traceback()

def disable_traceback():
    """ enables tracebacks to be added to exception raises """
    tb_controls.disable_traceback()

def traceback_steps(trace_text):
    """ this generates the steps in a traceback
        usage:
            traceback_steps(traceback.format_exc())
    """
    # get rid of the first line with traceback
    trace_text = ('\n'.join(trace_text.splitlines()[1:-1]))
    # split the text into traceback steps
    file_lines = [i for i in trace_text.splitlines() if i.startswith('  File "') and '", line' in i]
    # build the output
    out = []
    for i in trace_text.splitlines():
        if i in file_lines:
            if len(out):
                yield '\n'.join(out)
            out = [i]
        else:
            out.append(i)
    yield '\n'.join(out)

def format_error_message(f_name, err_msg, trace_text, evil_args):
    top_line = " battle_tested crashed {f_name:}() ".format(f_name=f_name)
    while len(top_line) < 79:
        top_line = "-{}-".format(top_line)
    top_line = '\n\n{}'.format(top_line)
    bottom_line = '-'*len(top_line)

    break_path = trace_text.split('"')[1]
    break_line_number = int(trace_text.split(',')[1].split(' ')[-1])
    break_line_number_up = break_line_number-1
    break_line_number_down = break_line_number+1

    out = """{top_line:}

Error Message:

   {err_msg:}

Breakpoint: {break_path:} - line {break_line_number:}""".format(
        top_line=top_line,
        err_msg=err_msg,
        break_path=break_path,
        break_line_number=break_line_number
    )

    try:
        with open(break_path) as f:
            for i, line in enumerate(f):
                i+=1
                if i == break_line_number_up:
                    line_above=line.replace('\n','')
                if i == break_line_number:
                    break_line=line.replace('\n','')
                if i == break_line_number_down:
                    line_below=line.replace('\n','')

        out += """
  {break_line_number_up:>{num_len:}}|{line_above:}
->{break_line_number:>{num_len:}}|{break_line:}
  {break_line_number_down:>{num_len:}}|{line_below:}""".format(
            break_line_number_up=break_line_number_up,
            break_line_number=break_line_number,
            break_line_number_down=break_line_number_down,
            line_above=line_above,
            line_below=line_below,
            break_line=break_line,
            num_len=len(str(break_line_number_down))+1
        )
    except Exception as ex:
        # i only want this part if the whole file read works
        raise ex
        #pass
    out += """
To reproduce this error, run:

   {f_name:}{evil_args:}

{bottom_line:}
""".format(
        bottom_line=bottom_line,
        f_name=f_name,
        evil_args=evil_args,
        )
    return out


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
            try:
                fn(*arg_list)
            except Exception as ex:
                """error_string = ("{}\nbattle_tested crashed {} with:\n\n  {}{}\n\nError Message - {}\n{}".format(
                    '-'*(80-(len(type(ex).__name__)+2)),
                    fn.__name__,
                    fn.__name__,
                    (tuple(arg_list) if len(arg_list)>1 else '({})'.format(arg_list[0])),
                    (ex.message if 'message' in dir(ex) else ex.args[0]),
                    '-'*80))"""
                # get the step where the code broke

                tb_steps_full = [i for i in traceback_steps(traceback.format_exc())]
                tb_steps_with_func_name = [i for i in tb_steps_full if i.splitlines()[0].endswith(fn.__name__)]

                if len(tb_steps_with_func_name)>0:
                    tb = tb_steps_with_func_name[-1]
                else:
                    tb = tb_steps_full[-1]

                error_string = format_error_message(
                    fn.__name__,
                    '{} - {}'.format(type(ex).__name__,(ex.message if 'message' in dir(ex) else ex.args[0])),
                    tb,
                    (tuple(arg_list) if len(arg_list)>1 else '({})'.format(repr(arg_list[0])))
                )

                ex.message = error_string
                ex.args = error_string,
                print('total tests: {}'.format(next(count)-1))
                raise ex

        # run the test
        try:
            fuzz()
        finally:
            interval.stop()
            gc_interval.stop()

        print('battle_tested: no falsifying examples found')
        print('total tests: {}'.format(next(count)-1))

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

# make fuzz its own independent function
fuzz = battle_tested.fuzz

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
        # this one blows up on purpose
        return input_arg+1

    #fuzz(lambda i:i+1)
    #fuzz(sample3, seconds=10)

    print('finished running battle_tested.py')

