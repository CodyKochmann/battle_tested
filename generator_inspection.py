from __future__ import print_function
from sys import stderr

def tee(pipeline, name, output_function=print):
    if isinstance(output_function, file):
        _old=output_function
        output_function = lambda i:_old.write(str(i))
    for i in pipeline:
        output_function(i)
        yield i

odd_collection = []

g = (i for i in range(100))
#g = tee(g, 'beginning')
g = (i for i in g if i%2)
g = tee(g, 'only_odds', stderr)
g = (i for i in g if i%3==0)
g = tee(g, 'only_divisible_by_3', odd_collection.append)

for i in g:
    print('final -',i)

print(odd_collection)
