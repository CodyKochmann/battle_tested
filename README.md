# battle_tested
A decorator that puts functions through hell so in production your code will have already seen worse.


## Example Usage

```
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


print('finished running battle_tested.py')
```
