#!/bin/bash
# tests battle_tested in ipython
#
echo "from battle_tested import fuzz, crash_map, success_map
fuzz(lambda i:i+1)
fuzz(lambda i:i+1, keep_testing=True)
crash_map()
success_map()
def sample(a):return a+' world'
fuzz(sample)
fuzz(sample, keep_testing=True)
crash_map()
success_map()
" | ipython
