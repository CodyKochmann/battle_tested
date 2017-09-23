

from hypothesis import strategies as st
from random import choice
from re import findall




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
                    'exit("######## WARNING this code is executing strings blindly ########")'
                ]
            ), 0
        )

    @staticmethod
    def bools():
        return iter(partial(choice, (True, False)), '')

    @staticmethod
    def ints():
        """# fish
                                for i in range(1,20):
                                    yield i
                                # sticks
                                for i in range(-10,0):
                                    yield i"""
        # waffles
        #for i in iter(partial(choice, [2**n for n in range(33)]), ''):
        #    yield i
        for i in iter(partial(randint, 2, 2**32),''):
            yield i

with open('random_ish.txt','wb') as f:
    g = easy.ints()
    for i in range(1000):
        i=next(g)
        print(i)
        f.write(i.to_bytes(4, 'little'))
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
for i in range(5000):
    i = next(g)
    print(i)
    try:
        eval(i)
    except Exception as e:
        print(e)
        pass
"""
exit()

for i in range(10):
    print(st.characters().example(), chars())
"""


