# -*- coding: utf-8 -*-
# @Author: CodyKochmann
# @Date:   2020-04-05 11:39:37
# @Last Modified by:   CodyKochmann
# @Last Modified time: 2020-04-05 12:23:59

from typing import Set, Tuple, Dict
import sqlite3, inspect, logging, unittest

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

class FuzzResultDB(sqlite3.Connection):
	schema = [
		'''
			CREATE TABLE IF NOT EXISTS fuzz_tests (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				target_module TEXT,
				target_function_name TEXT,
				target_function_repr TEXT,
				target_function_source TEXT
			);
		''',
		'''
			CREATE TABLE IF NOT EXISTS test_ingest (
				test_id INTEGER REFERENCES fuzz_tests(id),
				successful BOOLEAN NOT NULL,
				input_types TEXT NOT NULL,
				input_args TEXT NOT NULL,
				output_type TEXT,
				output TEXT,
				exception_type TEXT,
				exception_message TEXT,
				CHECK (
					(
						output_type != NULL AND output != NULL
					) OR (
						exception_type != NULL AND exception_message != NULL
					)
				)
			);
		'''
	]

	def __init__(self, fuzz_target, fuzz_result: Dict, db_path=":memory:"):
		# validate input
		assert callable(fuzz_target), f'FuzzResultDB assumes fuzz_target is some type of calable function - {fuzz_target}'
		assert isinstance(fuzz_result, dict), f'FuzzResultDB assumes fuzz_result will be a dict - {fuzz_result}'
		assert isinstance(db_path, str), f'FuzzResultDB assumes db_path will be a string - {db_path}'
		# initialize sqlite3.Connection components
		sqlite3.Connection.__init__(self, db_path)
		# save input for potential future reference
		self._db_path = db_path
		self._fuzz_target = fuzz_target
		self._fuzz_result = fuzz_result
		# load the base schema
		self.load_schema()
		# save the fuzz results
		self.save_results(fuzz_target, fuzz_result)

	def load_schema(self):
		cursor = self.cursor()
		for command in FuzzResultDB.schema:
			try:
				list(cursor.execute(command))
			except Exception as ex:
				logging.exception('failed to run sql command - %', command)
				raise ex
		cursor.close()

	@property
	def test_id(self):
		if not hasattr(self, '_test_id'):
			cursor = self.cursor()
			self._test_id = cursor.execute(
				'''
					INSERT INTO fuzz_tests (
						target_module,
						target_function_name,
						target_function_repr,
						target_function_source
					) VALUES (?, ?, ?, ?);
				''',
				(
					self._fuzz_target.__module__ if hasattr(self._fuzz_target, '__module__') else None,
					self._fuzz_target.__name__ if hasattr(self._fuzz_target, '__name__') else None,
					repr(self._fuzz_target),
					attempt_getsource(self._fuzz_target)
				)
			).lastrowid
			cursor.close()
		return self._test_id

	def save_results(self, fuzz_target, fuzz_result):
		cursor = self.cursor()
		cursor.execute('begin')
		# iterate through the FuzzResult to store its tests to the db
		for type_combo, result in fuzz_result.items():
			unittest.TestCase.assertEquals(unittest.TestCase(), [type(type_combo), type(result)], [tuple, dict])
			assert len(result) > 0, result
			assert len(result) <= 2, result
			if True in result and len(result[True]) > 0: # successful tests need to be stored
				list(cursor.executemany(
					'''
						INSERT INTO test_ingest (
							test_id,
							successful,
							input_types,
							input_args,
							output_type,
							output
						) VALUES (?, ?, ?, ?, ?, ?);
					''',
					(
						(
							self.test_id,
							True,
							repr(type_combo),
							repr(input_args),
							repr(type(output)), 
							repr(output)
						)
						for input_args, output in result[True]
					)
				))
			if False in result and len(result[False]) > 0: # failed tests need to be stored
				for exception, exception_message in result[False]:
					list(cursor.executemany(
						'''
							INSERT INTO test_ingest (
								test_id,
								successful,
								input_types,
								input_args,
								exception_type,
								exception_message
							) VALUES (?, ?, ?, ?, ?, ?);
						''',
						(
							(
								self.test_id,
								False,
								repr(type_combo),
								repr(input_args),  # (type(output), output.args) or (ex_type, ex_message)
								repr(exception),
								exception_message[0] if isinstance(exception_message, tuple) and len(exception_message) == 1 and isinstance(exception_message[0], str) and len(exception_message[0].strip()) > 0 else repr(exception_message)
							)
							for input_args in result[False][(exception, exception_message)]
						)
					))					
		cursor.execute('commit')
		cursor.close()

	def save_to_file(self, file_path):
		''' this function saves the FuzzResultDB to a file on the filesystem '''
		assert isinstance(file_path, str), file_path
		cursor = self.cursor()
		cursor.execute("vacuum main into ?", (file_path,))
		cursor.close()


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
	