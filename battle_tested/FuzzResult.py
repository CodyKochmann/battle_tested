# -*- coding: utf-8 -*-
# @Author: CodyKochmann
# @Date:   2020-04-05 11:39:37
# @Last Modified by:   CodyKochmann
# @Last Modified time: 2020-04-05 12:23:59

from typing import Set, Tuple


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

