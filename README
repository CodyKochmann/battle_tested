# battle_tested.py
An automated library that puts functions through hell so in production your code will have already seen worse.

## How to install it?

```
pip install --user battle_tested
```

## iPython Demo

```python
In [1]: from battle_tested import battle_tested
WARNING: better_exceptions will only inspect code from the command line
         when using: `python -m better_exceptions'. Otherwise, only code
         loaded from files will be inspected!

In [2]: def test(a):
   ...:     return a,a
   ...:

In [3]: battle_tested.fuzz(test)
testing: test
tests: 163          speed: 1622/sec  avg: 1622
tests: 872          speed: 1755/sec  avg: 1688
tests: 1365         speed: 1739/sec  avg: 1705
tests: 1798         speed: 1711/sec  avg: 1706
tests: 2489         speed: 1687/sec  avg: 1702
tests: 3058         speed: 1659/sec  avg: 1695
battle_tested: no falsifying examples found
In [4]:
```

## More Example Usage

```python
from battle_tested import battle_tested

@battle_tested(default_output=[], verbose=True, seconds=1, max_tests=5)
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

battle_tested.fuzz(sample3, verbose=True)
```
