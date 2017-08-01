# battle_tested.py
An automated library that puts functions through hell so in production your code will have already seen worse.

## How to install it?

```
pip install --user battle_tested
```

## iPython Demo

```python
In [1]: from battle_tested import fuzz

In [2]: def test(a):
   ...:     return int(a)
   ...:

In [3]: fuzz(test)
testing: test()
tests: 201          speed: 702/sec  avg: 702
tests: 484          speed: 893/sec  avg: 798
tests: 733          speed: 921/sec  avg: 839
tests: 975          speed: 919/sec  avg: 859
tests: 1138         speed: 864/sec  avg: 860
tests: 1368         speed: 858/sec  avg: 860
tests: 1681         speed: 906/sec  avg: 866
total tests: 1862
fuzzing test() found:
+------------------------+---------+
|   crash_input_types    |    12   |
|    exception_types     |    3    |
|    iffy_input_types    |    4    |
|      output_types      |    1    |
| successful_input_types |    4    |
|     unique_crashes     |    3    |
+------------------------+---------+
Out[3]:
+------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
|                        | +---------------------------------------------------------------+                                                                    |
|                        | |                        <class 'bytes'>                        |                                                                    |
|                        | |                        <class 'tuple'>                        |                                                                    |
|                        | |           <class 'hypothesis.types.RandomWithSeed'>           |                                                                    |
|                        | |                         <class 'dict'>                        |                                                                    |
|                        | |                        <class 'float'>                        |                                                                    |
| crash_input_types      | |                       <class 'complex'>                       |                                                                    |
|                        | |                       <class 'NoneType'>                      |                                                                    |
|                        | |                   <class 'decimal.Decimal'>                   |                                                                    |
|                        | |                         <class 'list'>                        |                                                                    |
|                        | | <class 'hypothesis.strategies.iterables.<locals>.PrettyIter'> |                                                                    |
|                        | |                         <class 'str'>                         |                                                                    |
|                        | |          <class 'hypothesis.strategies.RandomSeeder'>         |                                                                    |
|                        | +---------------------------------------------------------------+                                                                    |
|                        | +---------------+                                                                                                                    |
|                        | | OverflowError |                                                                                                                    |
| exception_types        | |   ValueError  |                                                                                                                    |
|                        | |   TypeError   |                                                                                                                    |
|                        | +---------------+                                                                                                                    |
|                        | +---------------------------+                                                                                                        |
|                        | | <class 'decimal.Decimal'> |                                                                                                        |
| iffy_input_types       | |       <class 'str'>       |                                                                                                        |
|                        | |      <class 'float'>      |                                                                                                        |
|                        | |      <class 'bytes'>      |                                                                                                        |
|                        | +---------------------------+                                                                                                        |
|                        | +---------+                                                                                                                          |
| output_types           | |   int   |                                                                                                                          |
|                        | +---------+                                                                                                                          |
|                        | +------------------------------+                                                                                                     |
|                        | |        <class 'int'>         |                                                                                                     |
| successful_input_types | |        <class 'bool'>        |                                                                                                     |
|                        | | <class 'fractions.Fraction'> |                                                                                                     |
|                        | |     <class 'uuid.UUID'>      |                                                                                                     |
|                        | +------------------------------+                                                                                                     |
|                        | +-------------------------+------------+----------+--------------------------------------------------------------------------------+ |
|                        | | exception type          | arg types  | location | crash message                                                                  | |
|                        | +-------------------------+------------+----------+--------------------------------------------------------------------------------+ |
| unique_crashes         | | <class 'OverflowError'> | ('float',) | line 2   | 'cannot convert float infinity to integer'                                     | |
|                        | | <class 'TypeError'>     | ('dict',)  | line 2   | "int() argument must be a string, a bytes-like object or a number, not 'dict'" | |
|                        | | <class 'ValueError'>    | ('bytes',) | line 2   | "invalid literal for int() with base 10: b'\\x94\\x94n-\\x81'"                 | |
|                        | +-------------------------+------------+----------+--------------------------------------------------------------------------------+ |
+------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
```

## More Example Usage

```python
from battle_tested import battle_tested, fuzz

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

fuzz(sample3, seconds=5, verbose=True)
```
