# Battle Tested

[![Downloads](https://pepy.tech/badge/battle-tested)](https://pepy.tech/project/battle-tested)
[![Downloads](https://pepy.tech/badge/battle-tested/month)](https://pepy.tech/project/battle-tested)
[![Downloads](https://pepy.tech/badge/battle-tested/week)](https://pepy.tech/project/battle-tested)
[![Known Vulnerabilities](https://snyk.io//test/github/CodyKochmann/battle_tested/badge.svg?targetFile=requirements.txt)](https://snyk.io//test/github/CodyKochmann/battle_tested?targetFile=requirements.txt)

Fully automated python fuzzer built to test if code actually is production ready in seconds.

## How to install it?

```
pip install --user battle_tested
```

## What does this tool solve?

Python allows you to do pretty much whatever you want. This is a good thing for the most part however it creates the opportunity for unexpected events to occur. One of `battle_tested`'s strongest assets is its ability to show you all of those possibilities so there are no surprises. In a way, it surpasses learning about the behavior of code by reading docstrings because all behaviors are recorded during a fuzz.

For example, the image below shows just how much is brought to light about a piece of code without needing to read a textbook's worth of documentation (which almost never exists) just to learn about the full behavior of a single function.

![fuzz test questions](https://bit.ly/bt_readme_example)

## iPython Demo

```python
Python 3.6.1 (default, Apr  4 2017, 09:40:51)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.1.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from battle_tested import fuzz

In [2]: def test(a):
   ...:     return int(a)
   ...:

In [3]: fuzz(test)
testing: test()
tests: 4865        1572/sec in 3s
fuzzing test() found:
+------------------------+---------+
|   crash_input_types    |    9    |
|    exception_types     |    3    |
|    iffy_input_types    |    3    |
|      output_types      |    1    |
| successful_input_types |    4    |
|     unique_crashes     |    3    |
+------------------------+---------+
Out[3]:
+------------------------+------------------------------------------------------------------------------------------------------------------------------+
|                        | +------------+                                                                                                               |
|                        | |  NoneType  |                                                                                                               |
|                        | |   bytes    |                                                                                                               |
|                        | |  complex   |                                                                                                               |
|                        | |    dict    |                                                                                                               |
| crash_input_types      | |   float    |                                                                                                               |
|                        | | PrettyIter |                                                                                                               |
|                        | |    list    |                                                                                                               |
|                        | |    str     |                                                                                                               |
|                        | |   tuple    |                                                                                                               |
|                        | +------------+                                                                                                               |
|                        | +---------------+                                                                                                            |
|                        | | OverflowError |                                                                                                            |
| exception_types        | |   TypeError   |                                                                                                            |
|                        | |   ValueError  |                                                                                                            |
|                        | +---------------+                                                                                                            |
|                        | +---------+                                                                                                                  |
|                        | |  bytes  |                                                                                                                  |
| iffy_input_types       | |  float  |                                                                                                                  |
|                        | |   str   |                                                                                                                  |
|                        | +---------+                                                                                                                  |
|                        | +---------+                                                                                                                  |
| output_types           | |   int   |                                                                                                                  |
|                        | +---------+                                                                                                                  |
|                        | +----------+                                                                                                                 |
|                        | |   bool   |                                                                                                                 |
| successful_input_types | | Fraction |                                                                                                                 |
|                        | |   int    |                                                                                                                 |
|                        | |   UUID   |                                                                                                                 |
|                        | +----------+                                                                                                                 |
|                        | +----------------+------------+-----------+--------------------------------------------------------------------------------+ |
|                        | | exception type | arg types  | location  | crash message                                                                  | |
|                        | +----------------+------------+-----------+--------------------------------------------------------------------------------+ |
| unique_crashes         | | OverflowError  | ('float',) | line 1168 | 'cannot convert float infinity to integer'                                     | |
|                        | | TypeError      | ('dict',)  | line 1168 | "int() argument must be a string, a bytes-like object or a number, not 'dict'" | |
|                        | | ValueError     | ('bytes',) | line 1168 | "invalid literal for int() with base 10: b'\\x88pv\\x0b\\xc7\\xa6\\xc1\\x83'"  | |
|                        | +----------------+------------+-----------+--------------------------------------------------------------------------------+ |
+------------------------+------------------------------------------------------------------------------------------------------------------------------+
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

## Contributors

| [<img src="https://avatars0.githubusercontent.com/u/6968406" width="75px;"/>](https://github.com/CodyKochmann) | [Cody Kochmann](https://github.com/CodyKochmann) | lead author |
|:---:|:--- |:--- |
| [<img src="https://avatars2.githubusercontent.com/u/1007" width="75px;"/>](https://github.com/marcinpohl) | [Marcin Pohl](https://github.com/marcinpohl) | advising for better performance and resource utilization |
