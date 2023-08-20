#!/usr/local/bin/env python3
# by: Cody Kochmann

# import beta fuzz
from battle_tested.beta import fuzz

# define a target we will fuzz
def my_adder(a, b):
    return a + b

# run the fuzz
result = fuzz(my_adder, max_tests=65536)

# save the result to a file
result.save_to_file('fuzz-result.db')

print('finished writing fuzz-result.db')

print('currently I am using sqlitebrowser to explore this database')

