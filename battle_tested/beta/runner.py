from itertools import cycle, chain, product
from collections import defaultdict, deque
from functools import partial
from contextlib import contextmanager
from pprint import pprint
from time import time
import gc

from battle_tested.beta.mutators import mutate
from battle_tested.beta.ammo import infinite_gc_ammo, standard
from battle_tested.beta.easy_street import easy_street
from battle_tested.beta.FuzzResult import FuzzResult
from battle_tested.beta.function_arg_count import function_arg_count
from battle_tested.beta.input_type_combos import input_type_combos


def fuzz_generator(input_type):
	''' this is the core function that creates test inputs to fuzz with.
		simply give it a type you want and it will use the mutation libraries
		to generate a little chaos for you to use.
	'''
	assert isinstance(input_type, type), input_type
	#for i in infinite_gc_ammo():
	#	yield from mutate(i, input_type)
	pipes = [infinite_gc_ammo(), easy_street.garbage()]
	pipes = chain.from_iterable(chain.from_iterable(cycle(product(pipes, repeat=len(pipes)))))
	standard_types = standard.types
	for i in pipes:
		if type(i) in standard.types:
			yield from mutate(i, input_type)


def runner(fn, input_types):
	''' this contains the logic for fuzzing a single type combo against a function
		to make it so you can balance which type combos will recieve more or less
		processing time purely through python generator logic/stepping
	'''
	fuzz_generators = map(fuzz_generator, input_types)
	for args in zip(*fuzz_generators):
		try:
			yield input_types, True,  args, fn(*args)
		except Exception as ex:
			yield input_types, False, args, ex


def fuzz_test(fn, input_type_combinations):
	''' this is the money shot of where the actual fuzzing is ran. '''
	# generate a "runner" for every input type combo
	test_runners = cycle(runner(fn, combo) for combo in input_type_combinations)

	# this data structure contains all of the information of the fuzz test
	result_map = defaultdict(
		lambda: {  # each type combo gets its own dict
			True: deque(maxlen=16),	# successful runs get stored as (args, output)
			False: defaultdict(		# each unique exception gets its own dict 
									#   exceptions are uniqued by the hash of the tuple of:
									#   (exception_type, exception_args)
				lambda: deque(maxlen=16)  # arguments that caused each crash are stored in tuples here 
			)
		}
	)
	# a simplified view of what this objects materialized form looks like is:
	#
	#{
	#	(int, int): {
	#		True: [
	#			([3, 5],  8),
	#			([1, 1],  2),
	#			([9, 15], 24),
	#		],
	#		False: {}
	#	}
	#	(set, str): {
	#		True: [],
	#		False: {
	#			(<class 'TypeError'>, ('can only concatenate str (not "set") to str',)): [
	#				({'yolo', {2, 4, 6}})
	#			]
	#		}
	#	}
	#}

	for tr in test_runners:
		input_types, success, args, output = next(tr)
		if success:
			# store the input, output pair in the successful runs
			result_map[input_types][success].append((args, output))
		else:
			# store the arguments in the deque for that specific exception
			result_map[input_types][success][(type(output), output.args)].append(args)
		# return the current state of the result map to let external logic
		# decide if its necessary to continue fuzzing.
		yield result_map

def quick_show_result(result):
	''' converts an optimized result object into something a little cleaner
		and pprints the simplified version.

		This will become a method of FuzzResult later.
	''' 
	assert isinstance(result, dict), type(result)
	pprint({k:{vk:list(vv) for vk, vv in v.items()} for k,v in result.items()})

@contextmanager
def no_gc():
	gc.disable()
	try:
		yield
	finally:
		gc.enable()
		gc.collect(2)


def run_fuzz(fn,
            *, # force settings to be kv pairs
            max_tests=100_000,
            seconds=6,  # note: might be solvable with generators.timed_pipeline
            input_types=tuple(),
            exit_on_first_crash=False,
            allow=tuple(),
            verbosity=1):
	with no_gc():
		start_time = time()
		input_types = tuple(
			input_type_combos(
				input_types if input_types else standard.types,
				function_arg_count(fn)
			)
		)
		result = None
		pipe = fuzz_test(fn, input_types)
		update_interval = int(max_tests/100)
		if verbosity <= 1:
			for i, v in zip(range(max_tests), pipe):
				if not i % update_interval:
					print(f'{i} / {max_tests}')
					print(FuzzResult(v))
					result = v
		else:
			for i, v in zip(range(max_tests), pipe):
				print(i)
				#quick_show_result(v)
				if not i % update_interval:
					print(f'{i} / {max_tests}')
					print(FuzzResult(v))
					result = v
		duration = time() - start_time
		print(f'fuzz duration for {fn}: {duration}s or {max_tests/duration} per sec')
		return result

def main():
	''' runs the fuzzer components through the basic movements to show how all
		the components would run in a primary fuzz() function
	'''
	fn = lambda a, b: a + b
	result = None
	#for i in fuzz_test(fn, tuple(product(standard.types, repeat=2))):
	for i, v in zip(range(100_000), fuzz_test(fn, tuple(product(standard.types, repeat=2)))):
		#pass
		if i%1000 == 0:
			print(i, 100_000)
			if i%10_000 == 0:
				print('-')
				print(FuzzResult(v))
				result = v
	return result


if __name__ == '__main__':
	main()
