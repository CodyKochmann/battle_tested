import itertools, json, string, sys, math
from functools import wraps, partial
from contextlib import suppress
from collections import deque, defaultdict
import operator
from base64 import b16encode, b32encode, b64encode, b64encode, a85encode

from generators import G, chain, window, first

eprint = partial(print, file=sys.stderr, flush=True)

standard_types = { bool, bytearray, bytes, complex, dict, float, int, list, set, str, tuple }
standard_defaults = [i() for i in standard_types]

printables = {k:v for k,v in enumerate(string.printable)}

small_int_cyclers = zip(*(itertools.cycle(range(1, i)) for i in range(2, 7)))
kinda_random_small_int = map(sum, small_int_cyclers)
kinda_random_medium_int = (a*b for a,b in zip(kinda_random_small_int, kinda_random_small_int))
kinda_random_big_int = (a*b for a,b in zip(kinda_random_medium_int, kinda_random_medium_int))

encoders = b16encode, b32encode, b64encode, b64encode, a85encode

str_encode_or_ignore = partial(str.encode, errors='ignore')
bytes_decode_or_ignore = partial(bytes.decode, errors='ignore')

def cached_uniq(pipe):
    cache = defaultdict(partial(deque, maxlen=4))
    for i in pipe:
        if i not in cache[type(i)]:
            cache[type(i)].append(i)
            yield i

def uniq(pipe):
    prev = next(pipe)
    for i in pipe:
        if type(i) == type(prev) and i == prev:
            continue
        else:
            yield i
            prev = i


def hashable(o):
    try:
        hash(o)
        return True
    except:
        return False

def hashable_or_none(o):
    '''returns an object if it is hashable or just None'''
    try:
        hash(o)
        return o
    except:
        return None

def flipped(fn):
    '''this decorator allows generators to yield their output and their flipped output'''
    assert callable(fn), fn
    def flip(o):
        if isinstance(o, str):
            return ''.join(reversed(o))
        elif isinstance(o, bytes):
            return bytes(bytearray(reversed(o)))
        elif isinstance(o, (bytearray, list, set, tuple)):
            return type(o)(reversed(o))
        else:
            raise Exception('this wasnt worth flipping: {}'.format(o))

    @wraps(fn)
    def wrapper(*a, **k):
        for i in fn(*a, **k):
            yield i
            yield flip(i)
    return wrapper

def map_attempt(fn, iterable):
    ''' this works just like map but filters out crashes '''
    assert callable(fn), fn
    iterable = iter(iterable)
    still_going = True
    while still_going:
        with suppress(Exception):
            for i in iterable:
                yield fn(i)
            still_going = False

def harvest_bool_from_bool(o):
    assert type(o) is bool, o
    yield not o
    yield o

def harvest_bytearray_from_bool(o):
    assert type(o) is bool, o
    yield bytearray(o)
    yield bytearray(not o)

def harvest_bytes_from_bool(o):
    assert type(o) is bool, o
    yield bytes(o)
    yield bytes(not o)

def harvest_complex_from_bool(o):
    assert type(o) is bool, o
    yield complex(o)
    yield complex(not o)

def harvest_dict_from_bool(o):
    assert type(o) is bool, o
    global standard_defaults
    for i in map(hashable_or_none, standard_defaults):
        yield {o:i}
        yield {i:o}
        yield {i:o, o:i}

def harvest_float_from_bool(o):
    assert type(o) is bool, o
    yield float(o)
    yield float(not o)

def harvest_int_from_bool(o):
    assert type(o) is bool, o
    yield int(o)
    yield int(not o)

def harvest_list_from_bool(o):
    assert type(o) is bool, o
    for i in range(1, 8):
        yield [o] * i

def harvest_set_from_bool(o):
    assert type(o) is bool, o
    yield {o}
    yield {not o}
    yield {o, not o}

def harvest_str_from_bool(o):
    assert type(o) is bool, o
    yield json.dumps(o)
    yield repr(o)
    int_o = int(o)
    yield str(int_o)
    yield bin(int_o)
    yield bytes(int_o).decode()

def harvest_tuple_from_bool(o):
    assert type(o) is bool, o
    yield from map(tuple, harvest_list_from_bool(o))

def harvest_bool_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from harvest_bool_from_bool(bool(o))
    for i in harvest_list_from_bytearray(o):
        if isinstance(i, int):
            yield from harvest_bool_from_int(i)

def harvest_bytearray_from_bytearray(o):
    assert type(o) is bytearray, o
    for i in range(1, 9):
        tmp = o * i
        yield tmp
        tmp.reverse()
        yield tmp

def harvest_bytes_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from map(bytes, harvest_bytearray_from_bytearray(o))

def harvest_complex_from_bytearray(o):
    assert type(o) is bytearray, o
    yield complex(len(o), len(o))
    yield from G(harvest_bytearray_from_bytearray(o)
        ).chain(
        ).window(2
        ).map(lambda i:[complex(i[0]), complex(i[1]), complex(*i)]
        ).chain()

def harvest_dict_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from harvest_dict_from_list(list(o))
    yield from harvest_dict_from_list(list(map(chr, o)))

def harvest_float_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from harvest_float_from_float(float(len(o) * len(o)))
    if o:
        for i in harvest_bytearray_from_bytearray(o):
            yield float.fromhex(o.hex())
            for ii in i:
                yield from harvest_float_from_int(i)

def harvest_int_from_bytearray(o):
    assert type(o) is bytearray, o
    for i in [o, o.upper(), o.lower()]:
        yield int.from_bytes(o, 'little')
        yield int.from_bytes(o, 'big')

@flipped
def harvest_list_from_bytearray(o):
    assert type(o) is bytearray, o
    for x in range(-1, 2):
        yield [i+x for i in o]
        yield [(i+x)%2 for i in o]
        yield [i+x for i in o if i%2]
        yield [i+x for i in o if not i%2]

def harvest_set_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from map(set, harvest_list_from_bytearray(o))

def harvest_str_from_bytearray(o):
    assert type(o) is bytearray, o
    for l in harvest_list_from_bytearray(o):
        with suppress(Exception):
            yield ''.join(map(chr, l))

def harvest_tuple_from_bytearray(o):
    assert type(o) is bytearray, o
    yield from map(tuple, harvest_list_from_bytearray(o))

def harvest_bool_from_bytes(o):
    assert type(o) is bytes, o
    yield from harvest_bool_from_int(len(o))
    for i in o:
        yield from (x=='1' for x in bin(i)[2:])

def harvest_bytearray_from_bytes(o):
    assert type(o) is bytes, o
    yield from map(bytearray, harvest_bytes_from_bytes(o))

def harvest_bytes_from_bytes(o):
    assert type(o) is bytes, o
    yield bytes(o)
    byte_pipe = lambda:map(lambda i:i%256, harvest_int_from_bytes(o))
    yield from map(bytes, byte_pipe())
    for ints in window(byte_pipe(), 8):
        for i in range(1, 8):
            yield bytes(ints[:i])
            yield bytes(ints[:i]) * i

def harvest_complex_from_bytes(o):
    assert type(o) is bytes, o
    yield from harvest_complex_from_int(len(o))
    for a, b in window(harvest_int_from_bytes(o), 2):
        yield complex(a, b)

def harvest_dict_from_bytes(o):
    assert type(o) is bytes, o
    for l in harvest_list_from_bytes(o):
        yield from harvest_dict_from_list(l)

def harvest_float_from_bytes(o):
    assert type(o) is bytes, o
    yield from harvest_float_from_list(list(o))
    for a, b in window(harvest_int_from_bytes(o), 2):
        yield float(a * b)

def harvest_int_from_bytes(o):
    assert type(o) is bytes, o
    yield from harvest_int_from_list(list(o))
    for i in o:
        yield from harvest_int_from_int(i)

@flipped
def harvest_list_from_bytes(o):
    assert type(o) is bytes, o
    yield [i for i in o]
    yield [bool(i) for i in o]
    yield [str(i) for i in o]
    yield [float(i) for i in o]

def harvest_set_from_bytes(o):
    assert type(o) is bytes, o
    yield from map(set, harvest_list_from_bytes(o))

def harvest_str_from_bytes(o):
    assert type(o) is bytes, o
    for b in harvest_bytes_from_bytes(o):
        yield bytes_decode_or_ignore(b)

def harvest_tuple_from_bytes(o):
    assert type(o) is bytes, o
    yield from map(tuple, harvest_list_from_bytes(o))

def harvest_bool_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_bool_from_float(o.imag)
    yield from harvest_bool_from_float(o.real)

def harvest_bytearray_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_bytearray_from_float(o.imag)
    yield from harvest_bytearray_from_float(o.real)

def harvest_bytes_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_bytes_from_float(o.imag)
    yield from harvest_bytes_from_float(o.real)

def harvest_complex_from_complex(o):
    assert type(o) is complex, o
    for a, b in window(harvest_int_from_float(o.imag), 2):
        yield complex(a, b)
    for a, b in window(harvest_int_from_float(o.real), 2):
        yield complex(a, b)

def harvest_dict_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_dict_from_float(o.imag)
    yield from harvest_dict_from_float(o.real)

def harvest_float_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_float_from_float(o.imag)
    yield from harvest_float_from_float(o.real)

def harvest_int_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_int_from_float(o.imag)
    yield from harvest_int_from_float(o.real)

def harvest_list_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_list_from_float(o.imag)
    yield from harvest_list_from_float(o.real)

def harvest_set_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_set_from_float(o.imag)
    yield from harvest_set_from_float(o.real)

def harvest_str_from_complex(o):
    assert type(o) is complex, o
    yield from harvest_str_from_float(o.imag)
    yield from harvest_str_from_float(o.real)

def harvest_tuple_from_complex(o):
    assert type(o) is complex, o
    yield from map(tuple, harvest_list_from_complex(o))

def remutate_dict(o, output_type):
    assert type(o) is dict, o
    assert output_type in standard_types
    if not o:
        yield output_type()
    for k, v in o.items():
        if type(k) in standard_types:
            yield from mutate(k, output_type)
        if not isinstance(v, dict) and type(v) in standard_types: # prevent infinite mutations
            yield from mutate(v, output_type)

def harvest_bool_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, bool)

def harvest_bytearray_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, bytearray)

def harvest_bytes_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, bytes)

def harvest_complex_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, complex)

def harvest_dict_from_dict(o):
    assert type(o) is dict, o
    for key_subset in harvest_list_from_list(list(o.keys())):
        yield {k:o[k] for k in key_subset}

def harvest_float_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, float)

def harvest_int_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, int)

@flipped
def harvest_list_from_dict(o):
    assert type(o) is dict, o
    yield list(o.keys())
    yield list(o.values())

def harvest_tuple_from_dict(o):
    assert type(o) is dict, o
    yield from map(tuple, harvest_list_from_dict(o))

def harvest_set_from_dict(o):
    assert type(o) is dict, o
    yield set(o.keys())
    yield from harvest_set_from_list(list(o.values()))

def harvest_str_from_dict(o):
    assert type(o) is dict, o
    yield from remutate_dict(o, str)

def harvest_bool_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield from harvest_bool_from_int(i)

def harvest_bytearray_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield from harvest_bytearray_from_int(i)

def harvest_bytes_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield from harvest_bytes_from_int(i)

def harvest_complex_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield from harvest_complex_from_int(i)

def harvest_dict_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield from harvest_dict_from_int(i)

def harvest_float_from_float(o):
    assert type(o) is float, o
    for i in harvest_int_from_float(o):
        yield o * i
        yield o + i
        yield o - i
        yield i - o

def harvest_int_from_float(o):
    assert type(o) is float, o
    try:
        o = o.as_integer_ratio()
        yield from chain(map(harvest_int_from_int, o))
    except (ValueError, OverflowError) as e:
        yield from harvest_int_from_int(1)

def harvest_list_from_float(o):
    assert type(o) is float, o
    try:
        a, b = o.as_integer_ratio()
    except (ValueError, OverflowError) as e:
        a, b = 1, 2
    aa = abs(min(512, a))
    bb = abs(min(512, b))
    yield from harvest_list_from_list([o])
    try:
        yield [o] * aa
        yield [o] * aa
        yield [a] * bb
        yield [b] * aa
        yield [([o] * aa)] * bb
        yield [([o] * bb)] * aa
        yield [([o*a] * aa)] * bb
        yield [([o*a] * bb)] * aa
        yield [([o*b] * aa)] * bb
        yield [([o*b] * bb)] * aa
    except MemoryError:
        pass

def harvest_set_from_float(o):
    assert type(o) is float, o
    for l in harvest_list_from_float(o):
        yield from harvest_set_from_list(l)

def harvest_str_from_float(o):
    assert type(o) is float, o
    yield str(o)
    yield repr(o)
    yield from map(chr, map(lambda i:i%1114112, harvest_int_from_float(o)))

def harvest_tuple_from_float(o):
    assert type(o) is float, o
    yield from map(tuple, harvest_list_from_float(o))

def harvest_bool_from_int(o):
    assert type(o) is int, o
    yield o % 2 == 1
    yield o % 2 == 0
    yield from (x=='1' for x in bin(o))
    yield from (x=='1' for x in bin(o**2))

def harvest_bytearray_from_int(o):
    assert type(o) is int, o
    yield from map(bytearray, harvest_bytes_from_int(o))

def harvest_bytes_from_int(o):
    assert type(o) is int, o
    for ints in window(map(lambda i:i%256, harvest_int_from_int(o)), 8):
        yield from (bytes(ints[:i]) for i in range(1, 8))

def harvest_complex_from_int(o):
    assert type(o) is int, o
    for a, b in window(harvest_int_from_int(o), 2):
        yield complex(a, b)

def harvest_dict_from_int(o):
    assert type(o) is int, o
    for k, v in zip(harvest_str_from_int(o), harvest_int_from_int(o)):
        yield {k:v for _,k,v in zip(range(min(16, max(1, v))), harvest_str_from_str(k), harvest_int_from_int(v))}

def harvest_float_from_int(o):
    assert type(o) is int, o
    for a, b in window(harvest_int_from_int(o), 2):
        if a != 0:
            yield b / a
        if b != 0:
            yield a / b
        yield float(a * b)

def harvest_int_from_int(o):
    assert type(o) is int, o
    yield from (o+x for x in range(-10, 11))
    yield from (o//x for x in range(-10, -1))
    yield from (o//x for x in range(1, 11))
    yield from (int(o*x) for x in range(-10, 11))
    yield from (o%x for x in range(-10, -1))
    yield from (o%x for x in range(1, 11))

@flipped
def harvest_list_from_int(o):
    assert type(o) is int, o
    bin_o = bin(o)[2:]
    yield list(bin_o)
    as_bools = [i=='1' for i in bin_o]
    for i in range(1, len(as_bools)):
        yield as_bools[:i]
        yield as_bools[i:]
        yield [(not x) for x in as_bools[:i]]
        yield [(not x) for x in as_bools[i:]]

def harvest_set_from_int(o):
    assert type(o) is int, o
    yield from map(set, harvest_list_from_int(o))

def harvest_str_from_int(o):
    assert type(o) is int, o
    yield bin(o)
    yield json.dumps(o)
    chars = filter(bool, map_attempt(lambda i:(printables[i%len(printables)]), harvest_int_from_int(o)))
    for l in kinda_random_small_int:
        out = ''.join(c for _,c in zip(range(l), chars))
        if out:
            yield out
        else:
            break

def harvest_tuple_from_int(o):
    assert type(o) is int, o
    for i in harvest_list_from_int(o):
        yield tuple(i)
        yield tuple(set(i))

def harvest_bool_from_list(o):
    assert type(o) is list, o
    yield bool(o)
    len_o = len(o)
    for i in range(2,10):
        yield bool(len_o % i)
    as_bools = list(map(bool, o))
    yield from as_bools
    for i in as_bools:
        yield not i

def harvest_bytearray_from_list(o):
    assert type(o) is list, o
    yield from map(bytearray, harvest_bytes_from_list(o))

def harvest_bytes_from_list(o):
    assert type(o) is list, o
    yield from map_attempt(str_encode_or_ignore, harvest_str_from_list(o))

def harvest_complex_from_list(o):
    assert type(o) is list, o
    for a, b in window(harvest_int_from_list(o)):
        yield complex(a, b)

def harvest_dict_from_list(o):
    assert type(o) is list, o
    len_o = len(o)
    yield {len_o: None}
    yield {None: len_o}
    yield {'data': o}
    yield {'result': o}
    o = itertools.cycle(o)
    for i in range(1, int(len_o*2)):
        with suppress(Exception):
            yield {next(o):next(o) for _ in range(i)}

def harvest_float_from_list(o):
    assert type(o) is list, o
    yield float(len(o))
    pipe = iter(harvest_int_from_list(o))
    for a, b in zip(pipe, pipe):
        yield float(a * b)
        if b and a:
            yield a/b
            yield b/a

def harvest_int_from_list(o):
    assert type(o) is list, o
    yield from harvest_int_from_int(len(o))
    for fn in [len, int, ord]:
        yield from map_attempt(fn, o)
    yield from str_encode_or_ignore(repr(o))

@flipped
def harvest_list_from_list(o):
    assert type(o) is list, o
    yield o
    if o:
        for i in range(1, int(math.sqrt(len(o)))+1):
            yield [v for ii,v in enumerate(o) if not ii%i]
            yield [v for ii,v in enumerate(o) if ii%i]
        yield [i for i in o if i]
        yield [i for i in o if not i]

def harvest_set_from_list(o):
    assert type(o) is list, o
    for l in harvest_list_from_list(o):
        s = set(map(hashable_or_none, l))
        yield {i for i in s if i is not None}
        yield {i for i in s if i}
        yield s

def harvest_str_from_list(o):
    assert type(o) is list, o
    yield repr(o)
    for i in o:
        with suppress(Exception):
            yield i.decode() if isinstance(i, bytes) else str(i)
    yield from map(repr, o)
    for i in o:
        with suppress(Exception):
            as_bytes = bytes(i) if isinstance(i, int) else bytes(str(i), encoding='utf-8')
            for encoder in encoders:
                yield encoder(as_bytes).decode()
    for i in o:
        with suppress(Exception):
            yield json.dumps(i)

def harvest_tuple_from_list(o):
    assert type(o) is list, o
    yield from map(tuple, harvest_list_from_list(o))
    yield from map(tuple, harvest_set_from_list(o))

def harvest_bool_from_set(o):
    assert type(o) is set, o
    yield from harvest_bool_from_list(list(o))

def harvest_bytearray_from_set(o):
    assert type(o) is set, o
    yield from harvest_bytearray_from_list(list(o))

def harvest_bytes_from_set(o):
    assert type(o) is set, o
    yield from harvest_bytes_from_list(list(o))

def harvest_complex_from_set(o):
    assert type(o) is set, o
    yield from harvest_complex_from_list(list(o))

def harvest_dict_from_set(o):
    assert type(o) is set, o
    yield from harvest_dict_from_list(list(o))

def harvest_float_from_set(o):
    assert type(o) is set, o
    yield from harvest_float_from_list(list(o))

def harvest_int_from_set(o):
    assert type(o) is set, o
    yield from harvest_int_from_list(list(o))

@flipped
def harvest_list_from_set(o):
    assert type(o) is set, o
    yield from harvest_list_from_list(list(o))

def harvest_set_from_set(o):
    assert type(o) is set, o
    yield from harvest_set_from_list(list(o))

def harvest_str_from_set(o):
    assert type(o) is set, o
    yield from harvest_str_from_list(list(o))

def harvest_tuple_from_set(o):
    assert type(o) is set, o
    yield from map(tuple, harvest_list_from_set(o))

def harvest_bool_from_str(o):
    assert type(o) is str, o
    yield from harvest_bool_from_list(list(o))
    yield from (bool(ord(ch)%2) for ch in o)

def harvest_bytearray_from_str(o):
    assert type(o) is str, o
    yield from map(bytearray, harvest_bytes_from_str(o))

def harvest_bytes_from_str(o):
    assert type(o) is str, o
    yield from map(str.encode, harvest_str_from_str(o))

def harvest_complex_from_str(o):
    assert type(o) is str, o
    yield from harvest_complex_from_list(list(o))
    for a, b in window(harvest_int_from_str(o), 2):
        yield complex(a, b)

def harvest_dict_from_str(o):
    assert type(o) is str, o
    yield {o: None}
    yield {None: o}
    yield {o: o}
    yield {o: {o: None}}
    yield {o: {o: o}}
    yield from harvest_dict_from_dict({a:b for a,b in zip(*([iter(o)]*2))})

def harvest_float_from_str(o):
    assert type(o) is str, o
    yield from harvest_float_from_float(float(len(o)))
    for a, b in window(filter(bool, map(ord, o)), 2):
        yield a * b
        yield a / b
        yield b / a

def harvest_int_from_str(o):
    assert type(o) is str, o
    yield from harvest_int_from_int(len(o))
    yield from map(ord, o)

@flipped
def harvest_list_from_str(o):
    assert type(o) is str, o
    yield from harvest_list_from_list(list(o))
    yield from harvest_list_from_list(list(map(ord, o)))

def harvest_set_from_str(o):
    assert type(o) is str, o
    for l in harvest_list_from_str(o):
        yield from harvest_set_from_list(l)

def harvest_str_from_str(o):
    assert type(o) is str, o
    yield o.upper()
    yield o.lower()
    yield o.strip()
    common_chars = ['\n', '"', "'", ' ', '\t', '.', ',', ':']
    yield from (o.replace(old_char, new_char) for old_char, new_char in itertools.combinations(common_chars, 2) if old_char in o)
    yield ''.join(x for x in o if x.isnumeric())
    yield ''.join(x for x in o if not x.isnumeric())

def harvest_tuple_from_str(o):
    assert type(o) is str, o
    yield from map(tuple, harvest_list_from_str(o))

def harvest_bool_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_bool_from_bool(bool(o))
    yield from map(bool, o)

def harvest_bytearray_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_bytearray_from_list(list(o))

def harvest_bytes_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_bytes_from_list(list(o))

def harvest_complex_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_complex_from_list(list(o))

def harvest_dict_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_dict_from_list(list(o))

def harvest_float_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_float_from_list(list(o))

def harvest_int_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_int_from_list(list(o))

@flipped
def harvest_list_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_list_from_list(list(o))

def harvest_set_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_set_from_list(list(o))

def harvest_str_from_tuple(o):
    assert type(o) is tuple, o
    yield from harvest_str_from_list(list(o))

def harvest_tuple_from_tuple(o):
    assert type(o) is tuple, o
    yield from map(tuple, harvest_list_from_tuple(o))


mutation_map = {
    (bool, bool): harvest_bool_from_bool,
    (bool, bytearray): harvest_bytearray_from_bool,
    (bool, bytes): harvest_bytes_from_bool,
    (bool, complex): harvest_complex_from_bool,
    (bool, dict): harvest_dict_from_bool,
    (bool, float): harvest_float_from_bool,
    (bool, int): harvest_int_from_bool,
    (bool, list): harvest_list_from_bool,
    (bool, set): harvest_set_from_bool,
    (bool, str): harvest_str_from_bool,
    (bool, tuple): harvest_tuple_from_bool,
    (bytearray, bool): harvest_bool_from_bytearray,
    (bytearray, bytearray): harvest_bytearray_from_bytearray,
    (bytearray, bytes): harvest_bytes_from_bytearray,
    (bytearray, complex): harvest_complex_from_bytearray,
    (bytearray, dict): harvest_dict_from_bytearray,
    (bytearray, float): harvest_float_from_bytearray,
    (bytearray, int): harvest_int_from_bytearray,
    (bytearray, list): harvest_list_from_bytearray,
    (bytearray, set): harvest_set_from_bytearray,
    (bytearray, str): harvest_str_from_bytearray,
    (bytearray, tuple): harvest_tuple_from_bytearray,
    (bytes, bool): harvest_bool_from_bytes,
    (bytes, bytearray): harvest_bytearray_from_bytes,
    (bytes, bytes): harvest_bytes_from_bytes,
    (bytes, complex): harvest_complex_from_bytes,
    (bytes, dict): harvest_dict_from_bytes,
    (bytes, float): harvest_float_from_bytes,
    (bytes, int): harvest_int_from_bytes,
    (bytes, list): harvest_list_from_bytes,
    (bytes, set): harvest_set_from_bytes,
    (bytes, str): harvest_str_from_bytes,
    (bytes, tuple): harvest_tuple_from_bytes,
    (complex, bool): harvest_bool_from_complex,
    (complex, bytearray): harvest_bytearray_from_complex,
    (complex, bytes): harvest_bytes_from_complex,
    (complex, complex): harvest_complex_from_complex,
    (complex, dict): harvest_dict_from_complex,
    (complex, float): harvest_float_from_complex,
    (complex, int): harvest_int_from_complex,
    (complex, list): harvest_list_from_complex,
    (complex, set): harvest_set_from_complex,
    (complex, str): harvest_str_from_complex,
    (complex, tuple): harvest_tuple_from_complex,
    (dict, bool): harvest_bool_from_dict,
    (dict, bytearray): harvest_bytearray_from_dict,
    (dict, bytes): harvest_bytes_from_dict,
    (dict, complex): harvest_complex_from_dict,
    (dict, dict): harvest_dict_from_dict,
    (dict, float): harvest_float_from_dict,
    (dict, int): harvest_int_from_dict,
    (dict, list): harvest_list_from_dict,
    (dict, set): harvest_set_from_dict,
    (dict, str): harvest_str_from_dict,
    (dict, tuple): harvest_tuple_from_dict,
    (float, bool): harvest_bool_from_float,
    (float, bytearray): harvest_bytearray_from_float,
    (float, bytes): harvest_bytes_from_float,
    (float, complex): harvest_complex_from_float,
    (float, dict): harvest_dict_from_float,
    (float, float): harvest_float_from_float,
    (float, int): harvest_int_from_float,
    (float, list): harvest_list_from_float,
    (float, set): harvest_set_from_float,
    (float, str): harvest_str_from_float,
    (float, tuple): harvest_tuple_from_float,
    (int, bool): harvest_bool_from_int,
    (int, bytearray): harvest_bytearray_from_int,
    (int, bytes): harvest_bytes_from_int,
    (int, complex): harvest_complex_from_int,
    (int, dict): harvest_dict_from_int,
    (int, float): harvest_float_from_int,
    (int, int): harvest_int_from_int,
    (int, list): harvest_list_from_int,
    (int, set): harvest_set_from_int,
    (int, str): harvest_str_from_int,
    (int, tuple): harvest_tuple_from_int,
    (list, bool): harvest_bool_from_list,
    (list, bytearray): harvest_bytearray_from_list,
    (list, bytes): harvest_bytes_from_list,
    (list, complex): harvest_complex_from_list,
    (list, dict): harvest_dict_from_list,
    (list, float): harvest_float_from_list,
    (list, int): harvest_int_from_list,
    (list, list): harvest_list_from_list,
    (list, set): harvest_set_from_list,
    (list, str): harvest_str_from_list,
    (list, tuple): harvest_tuple_from_list,
    (set, bool): harvest_bool_from_set,
    (set, bytearray): harvest_bytearray_from_set,
    (set, bytes): harvest_bytes_from_set,
    (set, complex): harvest_complex_from_set,
    (set, dict): harvest_dict_from_set,
    (set, float): harvest_float_from_set,
    (set, int): harvest_int_from_set,
    (set, list): harvest_list_from_set,
    (set, set): harvest_set_from_set,
    (set, str): harvest_str_from_set,
    (set, tuple): harvest_tuple_from_set,
    (str, bool): harvest_bool_from_str,
    (str, bytearray): harvest_bytearray_from_str,
    (str, bytes): harvest_bytes_from_str,
    (str, complex): harvest_complex_from_str,
    (str, dict): harvest_dict_from_str,
    (str, float): harvest_float_from_str,
    (str, int): harvest_int_from_str,
    (str, list): harvest_list_from_str,
    (str, set): harvest_set_from_str,
    (str, str): harvest_str_from_str,
    (str, tuple): harvest_tuple_from_str,
    (tuple, bool): harvest_bool_from_tuple,
    (tuple, bytearray): harvest_bytearray_from_tuple,
    (tuple, bytes): harvest_bytes_from_tuple,
    (tuple, complex): harvest_complex_from_tuple,
    (tuple, dict): harvest_dict_from_tuple,
    (tuple, float): harvest_float_from_tuple,
    (tuple, int): harvest_int_from_tuple,
    (tuple, list): harvest_list_from_tuple,
    (tuple, set): harvest_set_from_tuple,
    (tuple, str): harvest_str_from_tuple,
    (tuple, tuple): harvest_tuple_from_tuple
}

for type_combo in itertools.product(standard_types, repeat=2):
    assert type_combo in mutation_map, type_combo

def mutate(o, output_type):
    ''' this function takes an input object and runs mutations on it to harvest
        inputs of the specified output type. this allows battle_tested to create
        more test inputs without needing to rely on random generation '''
    global mutation_map
    assert isinstance(mutation_map, dict), mutation_map
    assert all(type(k) is tuple for k in mutation_map), mutation_map
    assert all(len(k) is 2 for k in mutation_map), mutation_map
    assert all(all(type(t)==type for t in k) for k in mutation_map), mutation_map

    assert o is not type, o
    assert output_type in standard_types, output_type

    if o is None:
        o = False

    def mutator():
        if isinstance(o, output_type):
            for i in mutation_map[type(o), output_type](o):
                yield i
        else:
            for i in mutation_map[type(o), output_type](o):
                yield i
                yield from mutation_map[type(i), output_type](i)

    return cached_uniq(mutator())

def warn_about_duplicates(pipe):
    last = None
    count = 0
    current_dup = None
    for a, b in window(pipe, 2):
        if a == b and type(a) == type(b):
            current_dup = a
            count += 1
        elif count > 0:
            eprint('WARNING: found', count, 'duplicates of', repr(current_dup))
            count = 0
        yield a
        last = b
    yield last

def test_all_mutations():
    tests = len(standard_types) * len(standard_defaults)
    done = 0
    count = 0
    for start_variable in standard_defaults:
        for output_type in standard_types:
            ran = False
            done += 1
            eprint(done, '/', tests, 'testing harvest_{}_from_{}'.format(output_type.__name__, type(start_variable).__name__))
            for v in first(mutate(start_variable, output_type), 10000000):
                ran = True
                assert type(v) is output_type, v
                count += 1
            assert ran, locals()
    eprint('success: created', count, 'inputs')


if __name__ == '__main__':
    for _ in range(1):
        for c,i in enumerate(harvest_complex_from_bytearray(bytearray(b'hi'))):
            continue #print('-', i, type(i))
        for i in mutate({'name':'billy'}, int):
            continue #print(i)
        #print(c)
        for test in "hello world why don't we get some waffles or something? 7777".split(' '):
            for _type in (str, dict, list, bool, int, float):
                for i,v in enumerate(warn_about_duplicates(mutate(test, _type))):
                    continue #print(repr(v))
                #print(i)
    test_all_mutations()