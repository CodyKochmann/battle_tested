from itertools import product, cycle, islice
from random import shuffle
from re import findall
from string import ascii_letters, digits

import generators as gen

class easy_street:
    ''' This is a namespace for high speed test generation of various types '''

    @staticmethod
    def chars():
        test_chars = ascii_letters + digits
        for _ in gen.loop():
            for combination in product(test_chars, repeat=4):
                for i in combination:
                    yield i

    @staticmethod
    def strings():
        test_strings = [
            '',
            'exit("######## WARNING this code is executing strings blindly ########")'
        ]
        # this snippet rips out every word from doc strings
        test_strings += list(set(findall(
            r'[a-zA-Z\_]{1,}',
            [v.__doc__ for v in globals().values() if hasattr(v, '__doc__')].__repr__()
        )))

        for _ in gen.loop():
            for combination in product(test_strings, repeat=4):
                for i in combination:
                    yield i

    @staticmethod
    def bools():
        booleans = (True, False)
        for _ in gen.loop():
            for combination in product(booleans, repeat=4):
                for i in combination:
                    yield i

    @staticmethod
    def ints():
        numbers = tuple(range(-33,65))
        for _ in gen.loop():
            for combination in product(numbers, repeat=3):
                for i in combination:
                    yield i

    @staticmethod
    def floats():
        non_zero_ints = (i for i in easy_street.ints() if i != 0)
        stream1 = gen.chain(i[:8] for i in gen.chunks(non_zero_ints, 10))
        stream2 = gen.chain(i[:8] for i in gen.chunks(non_zero_ints, 12))
        for i in stream1:
            yield next(stream2)/(1.0*i)

    @staticmethod
    def lists():
        strategies = easy_street.strings(), easy_street.ints(), easy_street.floats(), easy_street.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(0, 21)))

        for _ in gen.loop():
            for length in lengths:
                for strat in strategies:
                    yield [st for st in islice(strat, length)]

    @staticmethod
    def tuples():
        for i in easy_street.lists():
            yield tuple(i)

    @staticmethod
    def dicts():
        strategies = easy_street.strings(), easy_street.ints(), easy_street.floats(), easy_street.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(1, 21)))

        for _ in gen.loop():
            for length in lengths:
                for strat in strategies:
                    yield { k:v for k,v in gen.chunks(islice(strat,length*2), 2) }

    @staticmethod
    def sets():
        strategies = easy_street.strings(), easy_street.ints(), easy_street.floats(), easy_street.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(0, 21)))

        for _ in gen.loop():
            for length in lengths:
                for strat in strategies:
                    yield {i for i in islice(strat, length)}

    @staticmethod
    def garbage():
        strategies = [
            easy_street.strings(),
            easy_street.ints(),
            easy_street.floats(),
            easy_street.bools(),
            easy_street.dicts(),
            easy_street.sets(),
            easy_street.lists(),
            easy_street.tuples()
        ]
        while 1:
            shuffle(strategies)
            for strat in gen.chain(product(strategies, repeat=len(strategies))):
                yield next(strat)

if __name__ == '__main__':
    for a,b in zip(range(1000000), easy_street.garbage()):
        pass #print(a,b)