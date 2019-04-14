from itertools import cycle, chain
from collections import defaultdict, deque
from functools import partial

def runner(fn, input_types):
	for args in FuzzGenerator(*input_types):
		try:
			yield input_types, True,  args, fn(*args)
		except Exception as ex:
			yield input_types, False, args, ex

def fuzz_test(fn, input_type_combinations):
	test_runners = cycle(runner(fn, combo) for combo in input_type_combinations)

	result_map = defaultdict(
		lambda: {
			True: deque(maxlen=16), 
			False: defaultdict(
				lambda: deque(maxlen=16)
			)
		}
	)

	for input_types, success, args, output in chain.from_iterable(test_runners):
		if success:
			# store the input, output pair in the successful runs
			result_map[input_types][success].append((args, output))
		else:
			# store the arguments in the deque for that specific exception
			result_map[input_types][success][output].append(args)
		# return the current state of the result map to let external logic
		# decide if its necessary to continue fuzzing.
		yield result_map




