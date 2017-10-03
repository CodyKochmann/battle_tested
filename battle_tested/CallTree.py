from pdb import Pdb
from io import StringIO
from functools import partial


class CallStep:

    __slots__ = ['pdb_text', 'hash']

    def __init__(self, pdb_text):
        assert pdb_text.startswith('> '), 'first line starts with > right????'
        assert pdb_text.splitlines()[1].startswith('-> '), 'second line starts with -> right??????'
        self.pdb_text = pdb_text

    def __str__(self):
        return 'CallStep({})'.format({
            'path':self.path,
            'name':self.name,
            'line':self.line,
            'return_value':self.return_value,
            'code':self.code
        })
    __repr__ = __str__

    def __hash__(self):
        if not hasattr(self, 'hash'):
            self.hash = hash(tuple((self.path,self.name,self.line,self.code)))
        return self.hash

    def __eq__(self, target):
        return type(target) == type(self) and hash(target) == hash(target)

    @property
    def _first_line(self):
        return self.pdb_text.splitlines()[0]
    @property
    def _second_line(self):
        return self.pdb_text.splitlines()[1]
    @property
    def _third_line(self):
        return self.pdb_text.splitlines()[2] if len(self.pdb_text.splitlines())>2 else ''

    @property
    def path(self):
        return self.pdb_text.split('(')[0].split('> ')[1]

    @property
    def line(self):
        return int(self.pdb_text.split('(')[1].split(')')[0])

    @property
    def code(self):
        return self._second_line.split('-> ')[1]

    @property
    def name(self):
        return self.pdb_text.split(')')[1].split('(')[0]

    @property
    def path_and_name(self):
        ''' shorthand helper for
                self.path + '-' + self.name
        '''
        return self.path + '-' + self.name

    @property
    def return_value(self):
        if '->' in self._first_line and len(self._first_line.split('->')[1]):
            return eval(self._first_line.split('->')[1]) # only doing this to see if it breaks anything
            #return self._first_line.split('->')[1]
        else:
            return None

    @property
    def has_return_value(self):
        return self.return_value is not None

class CallTree:
    def __init__(self, fn):
        ''' generate a CallTree with the given function '''
        assert callable(fn), 'CallTree needs a function as its argument, not {}'.format(fn)
        sio = StringIO()
        p = Pdb(stdout=sio)
        for i in range(512):
            p.cmdqueue.append('s')
        p.cmdqueue.append('q')
        p.runcall(fn)
        sio.seek(0)
        self.target_fn = fn
        self.pdb_text = sio.read()

    @property
    def call_steps(self):
        ''' takes the pdb_chunks and converts them to CallStep objects '''
        for i in self.pdb_chunks:
            yield CallStep(i)

    def print_pdb_chunks(self):
        ''' displays the steps extracted from running in pdb '''
        for i in self.pdb_chunks:
            print('')
            print(i)

    @property
    def pdb_chunks(self):
        ''' splits the pdb_output into chunked strings for each step '''
        for i in self.pdb_text.split('\n> '):
            yield i if i.startswith('> ') else '> {}'.format(i)

    def print_coverage(self):
        ''' returns a dict showing what line numbers have been executed from what functions '''
        out = {}
        unique_functions = {s.path+'-'+s.name for s in self.call_steps}
        unique_lines = set()
        for s in self.call_steps:
            unique_lines.add('{}-{}-{:06d}'.format(s.path,s.name,s.line))
        for i in sorted(unique_lines):
            print(i)

    @property
    def first_step(self):
        return next(self.call_steps)

    @property
    def target_call_path(self):
        return (i for i in self.call_steps if i.name == self.first_step.name)

    @property
    def target_lines_ran(self):
        return set(i.line for i in self.target_call_path)

    def __str__(self):
        return self.pdb_text.__str__()


if __name__ == '__main__':

    def my_function(i):
        # convert the input to a string
        i = str(i)
        if i: # if i is not an empty string
            # run this function again, with one less character
            return my_function(i[:-1])
        else:
            return i


    def function_lines_ran(fn):
        return CallTree(fn).target_lines_ran

    print(function_lines_ran(partial(my_function,329104)))

