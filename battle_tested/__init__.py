# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-04-27 12:49:17
# @Last Modified by:   cody
# @Last Modified time: 2017-05-26 13:44:21

"""
battle_tested - automated function fuzzer based on hypothesis to easily test production code

Example Usage:

    from battle_tested import battle_tested

    def test_function(a,b,c):
        return c,b,a

    battle_tested(test_function)

Or:

    from battle_tested import battle_tested

    @battle_tested()
    def test_function(a,b,c):
        return c,b,a

"""

from battle_tested import battle_tested
