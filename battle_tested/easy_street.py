

from random import choice
from re import findall

import generators as gen

from string import ascii_letters, digits
from functools import partial
from random import choice, randint
from itertools import product, cycle, chain, islice

def cycle_combinations(*gens):
    l_gen = len(gens)
    while 1:
        for i in chain(*product(gens, repeat=l_gen)):
            yield i

class easy_street:
    @staticmethod
    def chars():
        return iter(partial(choice, ascii_letters + digits), None )

    @staticmethod
    def strings():
        return iter(
            partial(
                choice,
                list(set(findall(r'[a-zA-Z\_]{1,}',[
                    v.__doc__ for v in globals().values() if hasattr(v, '__doc__')
                ].__repr__()))) + [
                    '',
                    'exit("######## WARNING this code is executing strings blindly ########")'
                ]
            ), 0
        )

    @staticmethod
    def bools():
        return iter(partial(choice, (True, False)), '')

    @staticmethod
    def ints():
        for i in iter(partial(choice, tuple(range(-33,65))), ''):
            yield i

    @staticmethod
    def floats():
        rand_numerator = (i for i in easy.ints() if i != 0)
        rand_denomerator = partial(next,(1.0*i for i in easy.ints() if i != 0))
        for n in rand_numerator:
            yield n/rand_denomerator()

    @staticmethod
    def lists():
        strategies = easy.strings(), easy.ints(), easy.floats(), easy.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(0, 21)))

        for _ in cycle([0]*300):
            for length in lengths:
                for strat in strategies:
                    yield [next(st) for st in islice(strat, length)]

    @staticmethod
    def tuples():
        for i in easy.lists():
            yield tuple(i)

    @staticmethod
    def dicts():
        strategies = easy.strings(), easy.ints(), easy.floats(), easy.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(0, 21)))

        for _ in cycle([0]*300):
            for length in lengths:
                for strat in strategies:
                    yield { next(k):next(v) for k,v in gen.chunks(islice(strat,length*2), 2) }

    @staticmethod
    def sets():
        strategies = easy.strings(), easy.ints(), easy.floats(), easy.bools()
        strategies = list(gen.chain(product(strategies, repeat=len(strategies))))
        lengths = cycle(list(range(0, 21)))

        for _ in cycle([0]*300):
            for length in lengths:
                for strat in strategies:
                    yield {next(i) for i in islice(strat, length)}

    @staticmethod
    def garbage():
        strategies = (
            easy.strings(),
            easy.ints(),
            easy.floats(),
            easy.bools(),
            easy.dicts(),
            easy.sets(),
            easy.lists(),
            easy.tuples()
        )
        while 1:
            for strats in product(strategies, repeat=len(strategies)):
                for strat in strats:
                    yield next(strat)





import generators as gen
rps=gen.performance_tools.runs_per_second

garbage = easy.tuples()

for i in range(5000):
    print(next(garbage))



class tmp:
    pass

print([getattr(easy, i)() for i in (x for x in dir(easy) if x not in dir(tmp))])

exit()

easy_garbage = (next(s) for s in iter(partial(choice, tuple(
    getattr(easy, i)() for i in (x for x in dir(easy) if x not in dir(tmp))
)), 500))



from inspect import getsource

_getsource = lambda fn:'\n'.join(getsource(fn).splitlines()[1:])
'''
for fn in sorted(dir(easy)):
    if fn.startswith('lists'):
        print('###', fn, '-', rps(getattr(easy, fn)()),'runs per second')
        print('')
        print('```')
        print(_getsource(getattr(easy, fn)))
        print('```')
        print('')

exit()


rps = gen.performance_tools.runs_per_second
'''

#for i in easy.lists():
#    print(i)


#exit()


if __name__ == '__main__':

    class tmp:
        pass

    easy_garbage = iter(partial(choice, tuple(
        getattr(easy, i)() for i in (x for x in dir(easy) if x not in dir(tmp))
    )), 500)

    e = lambda:next(next(easy_garbage))

    print(rps(easy_garbage))


    def my_add(a,b):
        return a+b

    from battle_tested import fuzz, storage


    def fill_storage():
        easy_garbage = iter(partial(choice, tuple(
            getattr(easy, i)() for i in (x for x in dir(easy) if x not in dir(tmp))
        )), 500)

        for i in easy_garbage:
            i = next(i)
            storage.test_inputs.append(i)
            yield i



    rps(fill_storage(), 0.08)

    fuzz(my_add,seconds=10)

    """

        for i in (x for x in dir(easy) if x not in dir(tmp)):
            g = getattr(easy, i)()
            print('----------------------\ntesting:',i,'\n----------------------')
            for i in range(10):
                print(next(g))

        exit()

        g = easy.chars()
        for i in range(10):
            print(next(g))

        g = easy.bools()
        for i in range(10):
            print(next(g))

        g = easy.ints()
        for i in range(50):
            print(next(g))


        g = easy.strings()
        for i in range(50):
            i = next(g)
            print(i)
        """
    """
        try:
            eval(i)
        except Exception as e:
            print(e)
            pass
        """
    """
    exit()

    for i in range(10):
        print(st.characters().example(), chars())
    """


