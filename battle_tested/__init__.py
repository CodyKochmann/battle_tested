# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-04-27 12:49:17
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2017-07-10 15:12:58

"""
battle_tested - automated function fuzzing library to quickly test production
                code to prove it is "battle tested" and safe to use.

Examples of Primary Uses:

    from battle_tested import fuzz

    def test_function(a,b,c):
        return c,b,a

    fuzz(test_function)
    # or to collect tests
    fuzz(test_function, keep_testing=True)

Or:

    from battle_tested import battle_tested

    @battle_tested()
    def test_function(a,b,c):
        return c,b,a

"""

from __future__ import print_function
from functools import wraps
from prettytable import PrettyTable
import logging
from hypothesis import given, strategies as st, settings, Verbosity
from gc import collect as gc
import traceback
import sys
from time import time
from stricttuple import stricttuple
from collections import deque

__all__ = 'battle_tested', 'fuzz', 'disable_traceback', 'enable_traceback', 'garbage', 'crash_map', 'success_map', 'results', 'stats', 'print_stats'

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

class UniqueCrashContainer(tuple):
    ''' a pretty printable container for crashes '''
    def __repr__(self):
        table = PrettyTable(('exception type','arg types','location','crash message'), sortby='exception type')
        table.align["exception type"] = "l"
        table.align["arg types"] = "l"
        table.align["location"] = "l"
        table.align["crash message"] = "l"
        for i in self:
            table.add_row((repr(i.err_type),repr(tuple(i.__name__ for i in i.arg_types)),[x for x in i.trace.split(', ') if x.startswith('line ')][-1],i.message))
        return table.get_string()

class PrettyTuple(tuple):
    ''' tuples with better pretty printing '''
    def __repr__(self):
        if len(self) > 0:
            table = PrettyTable(None)
            for i in self:
                if isinstance(i, tuple):
                    table.add_row(i)
                else:
                    if isinstance(i, type):
                        if hasattr(i, '__name__'):
                            i=i.__name__
                        else:
                            i=repr(i)
                    table.add_row((i,))
            return '\n'.join(table.get_string().splitlines()[2:])
        else:
            return str(self)

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

def traceback_file_lines(trace_text=None):
    """ this returns a list of lines that start with file in the given traceback
        usage:
            traceback_steps(traceback.format_exc())
    """
    # split the text into traceback steps
    return [i for i in trace_text.splitlines() if i.startswith('  File "') and '", line' in i]

def traceback_steps(trace_text=None):
    """ this generates the steps in a traceback
        usage:
            traceback_steps(traceback.format_exc())
    """
    if trace_text == None:
        trace_text = traceback.format_exc()
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

def traceback_text():
    """ this returns the traceback in text form """
    return('\n'.join(i for i in traceback_steps()))

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
        pass
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
            i = yield c
            if i is None:
                c += 1
            else:
                c += i

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

from io import StringIO
def run_silently(fn):
    """ runs a function silently with no stdout """
    stdout_holder = sys.stdout
    sys.stdout = StringIO()
    fn()
    sys.stdout = stdout_holder

class ipython_tools(object):
    """ tools to make battle_tested work with ipython nicely """
    detected = 'IPython' in sys.modules
    if detected:
        from IPython import get_ipython
        magic = get_ipython().magic
    @staticmethod
    def silence_traceback():
        'silences ipythons verbose debugging temporarily'
        if ipython_tools.detected:
            # this hijacks stdout because there is a print in ipython.magic
            run_silently(lambda:ipython_tools.magic("xmode Plain"))
    @staticmethod
    def verbose_traceback():
        're-enables ipythons verbose tracebacks'
        if ipython_tools.detected:
            ipython_tools.magic("xmode Verbose")


def function_arg_count(fn):
    """ generates a list of the given function's arguments """
    assert callable(fn), 'function_arg_count needed a callable function, not {0}'.format(repr(fn))
    return fn.__code__.co_argcount

class battle_tested(object):
    """
battle_tested - automated function fuzzing library to quickly test production
                code to prove it is "battle tested" and safe to use.

Examples of Primary Uses:

    from battle_tested import fuzz

    def test_function(a,b,c):
        return c,b,a

    fuzz(test_function)
    # or to collect tests
    fuzz(test_function, keep_testing=True)

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
    def __verify_tested__(fn):
        """ asserts that the function exists in battle_tested's results """
        battle_tested.__verify_function__(fn)
        assert fn in battle_tested._results.keys(), '{} was not found in battle_tested\'s results, you probably haven\'t tested it yet'.format(fn)

    @staticmethod
    def __verify_keep_testing__(keep_testing):
        """ ensures keep_testing is a valid argument """
        assert type(keep_testing) == bool, 'keep_testing needs to be a bool'
        assert keep_testing == True or keep_testing == False, 'invalid value for keep_testing'

    _results = {} # where all of the test results go.
    # results are composed like this
    # results[my_function]['unique_crashes']=[list_of_crashes]
    # results[my_function]['successes']=[list_of_successes]

    # safe container that holds crash results
    Crash = stricttuple(
        'Crash',
        arg_types = (
             lambda arg_types:type(arg_types)==tuple,
             lambda arg_types:len(arg_types)>0,
        ),
        args = (
            lambda args:type(args)==tuple,
            lambda args:len(args)>0,
        ),
        message = (
            lambda message:type(message) == str or message == None ,
        ),
        err_type = (
            lambda err_type:type(err_type)==type ,
        ),
        trace = (
            lambda trace:type(trace)==str ,
        )
    )

    # safe container that holds test results
    Result = stricttuple(
        'Result',
        successful_input_types = (
            lambda successful_input_types: type(successful_input_types)==PrettyTuple,
            lambda successful_input_types: all(type(i)==tuple for i in successful_input_types),
            lambda successful_input_types: all(all(isinstance(x,type) for x in i) for i in successful_input_types)
        ),
        crash_input_types = (
            lambda crash_input_types: type(crash_input_types)==PrettyTuple,
            lambda crash_input_types: all(type(i)==tuple for i in crash_input_types),
            lambda crash_input_types: all(all(isinstance(x,type) for x in i) for i in crash_input_types)
        ),
        iffy_input_types = (
            lambda iffy_input_types: type(iffy_input_types)==PrettyTuple,
            lambda iffy_input_types: all(type(i)==tuple for i in iffy_input_types),
            lambda iffy_input_types: all(all(isinstance(x,type) for x in i) for i in iffy_input_types)
        ),
        output_types = (
            lambda output_types: type(output_types)==PrettyTuple,
            lambda output_types: all(isinstance(i, type) for i in output_types),
        ),
        exception_types = (
            lambda exception_types: type(exception_types)==PrettyTuple,
            lambda exception_types: all(isinstance(i,Exception) or issubclass(i,Exception) for i in exception_types),
        ),
        unique_crashes = (
            lambda unique_crashes: type(unique_crashes)==UniqueCrashContainer,
        ),
    )

    @staticmethod
    def results(fn):
        '''returns the collected results of the given function'''
        battle_tested.__verify_tested__(fn)
        return battle_tested._results[fn]

    @staticmethod
    def stats(fn):
        ''' returns the stats found when testing a function '''
        results = battle_tested.results(fn)

        return {k:len(getattr(results, k)) for k in results._fields}

    @staticmethod
    def print_stats(fn):
        ''' prints the stats on a tested function '''
        stats = battle_tested.stats(fn)
        fn_name = fn.__name__ if '__name__' in dir(fn) else fn
        print('fuzzing {}() found:'.format(fn_name))
        t=PrettyTable(None)
        for k in sorted(stats.keys()):
            t.add_row((k,stats[k]))
        print('\n'.join(t.get_string().splitlines()[2:]))

    # these two are here so the maps can have doc strings
    class _crash_map(dict):
        '''a map of crashes generated by the previous test'''
    class _success_map(set):
        '''a map of data types that were able to get through the function without crashing'''
    crash_map = _crash_map()
    success_map = _success_map()

    @staticmethod
    def fuzz(fn, seconds=2, max_tests=1000000, verbose=False, keep_testing=False):
        """

fuzz - battle_tested's primary weapon for testing functions.

Example Usage:

    def my_function(a, b):
        ''' switches the variables '''
        return b, a

    fuzz(my_function)                     # runs a quick test to find breaks
    fuzz(my_function, keep_testing=True)  # runs tests and collects the outcomes
                                          # in `crash_map()` and `success_map()`

Parameters:

    fn           - the function to be fuzzed (must accept at least one argument)
    seconds      - maximum time battle_tested is allowed to fuzz the function
    max_tests    - maximum number of tests battle_tested will run before exiting
                   (if the time limit doesn't come first)
    verbose      - setting this to True dumps the parameters being tested to
                   stdout as they are being generated
    keep_testing - setting this to True allows battle_tested to keep testing
                   even after it finds the first falsifying example, the results
                   can be accessed with crash_map() and success_map()
"""
        battle_tested.__verify_function__(fn)
        battle_tested.__verify_seconds__(seconds)
        battle_tested.__verify_verbose__(verbose)
        battle_tested.__verify_max_tests__(max_tests)
        battle_tested.__verify_keep_testing__(keep_testing)

        args_needed = function_arg_count(fn)

        # generate a strategy that creates a list of garbage variables for each argument
        strategy = st.lists(elements=garbage, max_size=args_needed, min_size=args_needed)

        print('testing: {0}()'.format(fn.__name__))

        battle_tested.crash_map.clear()
        battle_tested.success_map.clear()

        count = generators.counter()
        average = generators.avg()
        timer = generators.timer()

        def print_stats(count, timer, average):
            per_second = count/timer
            print('tests: {:<12} speed: {}/sec  avg: {}'.format(int(count),int(per_second),int(average.send(per_second))))

        ipython_tools.silence_traceback()

        battle_tested._results[fn] = {
            'successful_input_types':deque(maxlen=500),
            'crash_input_types':set(),
            'iffy_input_types':set(), # types that both succeed and crash the function
            'output_types':set(),
            'exception_types':set(),
            'unique_crashes':dict()
        }

        interval = IntervalTimer(0.25, lambda:print_stats(count.send(0),next(timer),average))

        gc_interval = IntervalTimer(3, gc)

        @settings(timeout=seconds, max_examples=max_tests, verbosity=(Verbosity.verbose if verbose else Verbosity.normal))
        @given(strategy)
        def fuzz(arg_list):
            # make arg_list a tuple as a micro-optimization
            arg_list = tuple(arg_list)
            # unpack the arguments
            next(count)
            try:
                out = fn(*arg_list)
                # the rest of this block is handling logging a success
                input_types = tuple(type(i) for i in arg_list)
                # if the input types have caused a crash before, add them to iffy_types
                if input_types in battle_tested._results[fn]['crash_input_types']:
                    battle_tested._results[fn]['iffy_input_types'].add(input_types)
                # add the input types to the successful collection
                battle_tested._results[fn]['successful_input_types'].append(input_types)
                # add the output type to the output collection
                battle_tested._results[fn]['output_types'].add(type(out))
                battle_tested.success_map.add(tuple(type(i) for i in arg_list))
            except Exception as ex:
                # get the step where the code broke
                tb_steps_full = [i for i in traceback_steps()]
                tb_steps_with_func_name = [i for i in tb_steps_full if i.splitlines()[0].endswith(fn.__name__)]

                if len(tb_steps_with_func_name)>0:
                    tb = tb_steps_with_func_name[-1]
                else:
                    tb = tb_steps_full[-1]

                ex_message = ''
                if hasattr(ex, 'args') and len(ex.args)>0:
                    ex_message = ex.args[0]
                elif hasattr(ex, 'message') and len(ex.message)>0:
                    ex_message = ex.message

                error_string = format_error_message(
                    fn.__name__,
                    '{} - {}'.format(type(ex).__name__,ex_message),
                    tb,
                    (arg_list if len(arg_list)!=1 else '({})'.format(repr(arg_list[0])))
                )

                battle_tested._results[fn]['crash_input_types'].add(tuple(type(i) for i in arg_list))

                if keep_testing:
                    tb_text = traceback_text()
                    tb = '{}{}'.format(traceback_file_lines(tb_text),repr(type(ex)))
                    battle_tested.crash_map[tb]={'type':type(ex),'message':ex_message,'args':arg_list,'arg_types':tuple(type(i) for i in arg_list)}
                    battle_tested._results[fn]['unique_crashes'][tb]=battle_tested.Crash(
                        err_type=type(ex),
                        message=repr(ex_message),
                        args=arg_list,
                        arg_types=tuple(type(i) for i in arg_list),
                        trace=tb_text
                    )
                    battle_tested._results[fn]['exception_types'].add(type(ex))
                else:
                    ex.message = error_string
                    ex.args = error_string,
                    raise ex

        # run the test
        try:
            gc_interval.start()
            Timer(0.26,lambda:interval.start()).start()
            fuzz()
        finally:
            interval.stop()
            gc_interval.stop()

            results_dict = battle_tested._results[fn]
            results_dict['iffy_input_types'] = set(i for i in results_dict['crash_input_types'] if i in results_dict['successful_input_types'])

            battle_tested._results[fn] = battle_tested.Result(
                successful_input_types = PrettyTuple(set(i for i in results_dict['successful_input_types'] if i not in results_dict['iffy_input_types'] and i not in results_dict['crash_input_types'])),
                crash_input_types = PrettyTuple(results_dict['crash_input_types']),
                iffy_input_types = PrettyTuple(results_dict['iffy_input_types']),
                output_types = PrettyTuple(results_dict['output_types']),
                exception_types = PrettyTuple(results_dict['exception_types']),
                unique_crashes = UniqueCrashContainer(results_dict['unique_crashes'].values()),
            )
            ## find the types that both crashed and succeeded
            #results_dict['iffy_input_types'] = set(i for i in results_dict['crash_input_types'] if i in results_dict['successful_input_types'])
            ## clean up the unique_crashes section
            #results_dict['unique_crashes'] = tuple(results_dict['unique_crashes'].values())
            ## remove duplicate successful input types
            #results_dict['successful_input_types'] = set(results_dict['successful_input_types'])
            print('total tests: {}'.format(count.send(0)))
        if keep_testing:
            #examples_that_break = ('examples that break' if len(battle_tested.crash_map)>1 else 'example that broke')
            #print('found {} {} {}()'.format(len(battle_tested.crash_map),examples_that_break,fn.__name__))
            battle_tested.print_stats(fn)
            #print('run crash_map() or success_map() to access the test results')
        else:
            print('battle_tested: no falsifying examples found')
        return battle_tested._results[fn]


    def __call__(self, fn):
        """ runs before the decorated function is called """
        self.__verify_function__(fn)

        if fn not in battle_tested._results:
            # only test the first time this function is called
            if not ('skip_test' in self.kwargs and self.kwargs['skip_test']):
                # skip the test if it is explicitly turned off
                self.fuzz(fn, seconds=self.seconds, max_tests=self.max_tests, verbose=self.verbose)
            #self.tested = True

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
results = battle_tested.results
stats = battle_tested.stats
print_stats = battle_tested.print_stats

def crash_map():
    '''returns a map of crashes generated by the previous test'''
    return tuple(sorted(battle_tested.crash_map.values(), key=lambda i:i['type'].__name__))

def success_map():
    '''returns a map of data types that were able to get through the function without crashing'''
    return tuple(sorted(battle_tested.success_map, key=lambda i:i[0].__name__))

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

    # prove that successes of any type are possible
    fuzz(lambda i:i , keep_testing=True, seconds=10)

    #======================================
    #  Examples using the function syntax
    #======================================

    def sample3(input_arg):
        # this one blows up on purpose
        return input_arg+1

    #fuzz(lambda i:i+1)
    fuzz(sample3, seconds=120, keep_testing=True)
    crash_map()
    success_map()

    fuzz(lambda i:i)

    #======================================
    #   example harness
    #======================================
    def harness(key,value):
        global mydict
        global crash_examples
        global successful_types
        try:
            mydict[key]=value
            successful_types.add((type(key).name, type(value).name))
        except Exception as e:
            print('found one')
            crash_examples[e.args[0]]=(key,value)



    from pprint import pprint

    sample3_results = battle_tested.results(sample3)
    print(sample3_results.exception_types)

    print('fuzzing fuzz')
    fuzz(fuzz,keep_testing=True,seconds=10)

    #pprint(sample3_results)

    print('finished running battle_tested.py')
