

from hypothesis import strategies as st
from random import choice
from re import findall
from generators import window



from functools import partial
from random import choice, randint

print(dir(st))

basics = (
    st.binary(),
    st.booleans(),
    st.characters(),
    st.complex_numbers(),
    st.floats(),
    st.fractions(),
    st.integers(),
    st.none(),
    st.text(),
    st.uuids(),
    st.dictionaries(keys=st.text(), values=st.text())
)
from string import ascii_letters, digits
from functools import partial

class easy:
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
        rand_length = partial(randint, 0, 20)
        rand_list = partial(choice, (
            lambda:[next(easy.strings()) for i in range(rand_length())] ,
            lambda:[next(easy.ints()) for i in range(rand_length())] ,
            lambda:[next(easy.floats()) for i in range(rand_length())] ,
            lambda:[next(easy.bools()) for i in range(rand_length())] ,
        ))
        for i in iter(rand_list, ''):
            yield i()

    @staticmethod
    def tuples():
        for i in easy.lists():
            yield tuple(i)

    @staticmethod
    def dicts():
        rand_length = partial(randint, 0, 20)
        rand_dict = partial(choice, (
            lambda:{next(easy.strings()):next(easy.strings()) for i in range(rand_length())} ,
            lambda:{next(easy.ints()):next(easy.ints()) for i in range(rand_length())} ,
            lambda:{next(easy.floats()):next(easy.floats()) for i in range(rand_length())} ,
            lambda:{next(easy.bools()):next(easy.bools()) for i in range(randint(1,2))} ,
        ))
        for i in iter(rand_dict, ''):
            yield i()

    @staticmethod
    def sets():
        rand_length = partial(randint, 0, 20)
        rand_set = partial(choice, (
            lambda:{next(easy.strings()) for i in range(rand_length())} ,
            lambda:{next(easy.ints()) for i in range(rand_length())} ,
            lambda:{next(easy.floats()) for i in range(rand_length())} ,
            lambda:{next(easy.bools()) for i in range(randint(1,2))} ,
        ))
        for i in iter(rand_set, ''):
            yield i()

class tmp:
    pass


easy_garbage = iter(partial(choice, tuple(
    getattr(easy, i)() for i in (x for x in dir(easy) if x not in dir(tmp))
)), 500)

c = 500
for i in easy_garbage:
    c -= 1
    if c <= 0:
        break
    print(next(i))

exit()

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


