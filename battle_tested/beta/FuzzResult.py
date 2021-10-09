# -*- coding: utf-8 -*-
# @Author: CodyKochmann
# @Date:   2020-04-05 11:39:37
# @Last Modified by:   CodyKochmann
# @Last Modified time: 2020-04-05 12:23:59

from typing import Set, Tuple
import sqlite3, inspect

'''
FuzzResult structure

{
	(int, int): {
		True: [
			([3, 5],  8),
			([1, 1],  2),
			([9, 15], 24),
		],
		False: {}
	}
	(set, str): {
		True: [],
		False: {
			(<class 'TypeError'>, ('can only concatenate str (not "set") to str',)): [
				({'yolo', {2, 4, 6}})
			]
		}
	}
}
'''

def attempt_getsource(fn):
	try:
		return inspect.getsource(fn)
	except:
		return None

class FuzzResultDB:
	sql = []

	fuzz_tests = 'id, date, target_module, target_function_name' # basic references to tests
	sql.append('''
		CREATE TABLE IF NOT EXISTS fuzz_tests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			target_module TEXT,
			target_function_name TEXT,
			target_function_repr TEXT,
			target_function_source TEXT
		);
	''')

	# for now _just_ do string form, this will be serialized form later

	# successful tests
	# - test_id, input_types, output_type, input_args, output
	sql.append('''
		CREATE TABLE IF NOT EXISTS successful_tests (
			test_id INTEGER REFERENCES fuzz_tests(id),
			input_types TEXT NOT NULL,
			input_args TEXT NOT NULL,
			output_type TEXT NOT NULL,
			output TEXT NOT NULL,
			CHECK (input_types LIKE '(%)'),
			CHECK (input_args LIKE '(%)')
		);
	''')
	'test_id, type_combo, input_args, unique_error'
	# failed tests
	# - test_id, input_types, exception_type, input_args, output
	sql.append('''
		CREATE TABLE IF NOT EXISTS failed_tests (
			test_id INTEGER REFERENCES fuzz_tests(id),
			input_types TEXT NOT NULL,
			input_args TEXT NOT NULL,
			exception_type TEXT NOT NULL,
			exception TEXT NOT NULL,
			CHECK (input_types LIKE '(%)'),
			CHECK (input_args LIKE '(%)')
		);
	''')



class FuzzResult(dict):
	''' acts as a user friendly data structure to explore fuzz results '''

	@property
	def crash_input_types(self) -> Set[Tuple[type]]:
		return {k for k,v in self.items() if len(v[False]) > 0}
	
	@property
	def crash_input_count(self) -> int:
		return sum(len(v[False]) > 0 for v in self.values())
	
	@property
	def successful_input_types(self) -> Set[Tuple[type]]:
		return {k for k,v in self.items() if len(v[True]) > 0}

	@property
	def successful_input_count(self) -> int:
		return sum(len(v[True]) > 0 for v in self.values())

	@property
	def iffy_input_types(self) -> Set[Tuple[type]]:
		return self.crash_input_types.intersection(self.successful_input_types)

	@property
	def iffy_input_count(self) -> int:
		return sum(len(v[True]) > 0 and len(v[False]) > 0 for v in self.values())

	def __str__(self) -> str:
		return f'''
FuzzResult:
    type_combos:
        successful: {self.successful_input_count}
        problematic: {self.crash_input_count}
        iffy: {self.iffy_input_count}
		'''.strip()

	@property
	def sqlite(self) -> sqlite3.Connection:
		''' returns the FuzzResult in the form of a sqlite database '''
		assert hasattr(self, 'fuzz_target'), f'FuzzResult.sqlite needs you to set a fuzz_target first'
		# open a new sqlite db
		connection = sqlite3.connect(':memory:')
		# open a cursor to interact with it
		db = connection.cursor()
		# load up the db's schema
		for command in FuzzResultDB.sql:
			try:
				db.execute(command)
			except Exception as ex:
				logging.exception('failed to run sql command - %', command)
				raise ex
		# store the fuzz target
		test_id = db.execute(
			'''
				INSERT INTO fuzz_tests (
					target_module,
					target_function_name,
					target_function_repr,
					target_function_source
				) VALUES (?, ?, ?);
			''',
			(
				self.fuzz_target.__module__ if hasattr(self.fuzz_target, '__module__') else None,
				self.fuzz_target.__name__ if hasattr(self.fuzz_target, '__name__') else None,
				repr(self.fuzz_target),
				attempt_getsource(self.fuzz_target)
			)
		).lastrowid

		# iterate through the FuzzResult to store its tests to the db
		for type_combo, result in self.values():
			if True in result and len(result[True]) > 0: # successful tests need to be stored
				list(db.executemany(
					'''
						INSERT INTO successful_tests (
							test_id,
							input_types,
							input_args,
							output_type,
							output
						) VALUES (?, ?, ?, ?, ?);
					''',
					(
						(
							test_id,
							repr(type_combo),
							repr(input_args),
							repr(type(output)),
							repr(output)
						)
						for input_args, output in result[True]
					)
				))
			if False in result and len(result[False]) > 0: # failed tests need to be stored
				list(db.executemany(
					'''
						INSERT INTO failed_tests (
							test_id,
							input_types,
							input_args,
							exception_type,
							output
						) VALUES (?, ?, ?, ?, ?);
					''',(type(output), output.args)
					(
						(
							test_id,
							repr(type_combo),
							repr(input_args),
							repr(output[0]),
							repr(output[1])
						)
						for input_args, output in result[False]
					)
				))
		db.close()
		return connection
