import itertools, json, string
from functools import wraps, partial
from contextlib import suppress
from generators import G, chain
from base64 import b16encode, b32encode, b64encode, b64encode, a85encode

printables = {k:v for k,v in enumerate(string.printable)}

small_int_cyclers = zip(*(itertools.cycle(range(1, i)) for i in range(2, 7)))
kinda_random_small_int = map(sum, small_int_cyclers)
kinda_random_medium_int = (a*b for a,b in zip(kinda_random_small_int, kinda_random_small_int))
kinda_random_big_int = (a*b for a,b in zip(kinda_random_medium_int, kinda_random_medium_int))

encoders = b16encode, b32encode, b64encode, b64encode, a85encode

str_encode_or_ignore = partial(str.encode, errors='ignore')

def hashable(o):
    with suppress(Exception):
        hash(o)
        return True
    return False

def flipped(fn):
    '''this decorator allows generators to yield their output and their flipped output'''
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
    iterable = iter(iterable)
    still_going = True
    while still_going:
        with suppress(Exception):
            for i in iterable:
                yield fn(i)
            still_going = False

def harvest_bool_from_bool(o):
    yield not o
    yield o

def harvest_bytearray_from_bool(o):
    raise NotImplemented()

def harvest_bytes_from_bool(o):
    raise NotImplemented()

def harvest_complex_from_bool(o):
    raise NotImplemented()

def harvest_dict_from_bool(o):
    raise NotImplemented()

def harvest_float_from_bool(o):
    raise NotImplemented()

def harvest_int_from_bool(o):
    raise NotImplemented()

@flipped
def harvest_list_from_bool(o):
    raise NotImplemented()

def harvest_set_from_bool(o):
    raise NotImplemented()

def harvest_str_from_bool(o):
    raise NotImplemented()

def harvest_tuple_from_bool(o):
    raise NotImplemented()

def harvest_bool_from_bytearray(o):
    raise NotImplemented()

def harvest_bytearray_from_bytearray(o):
    raise NotImplemented()

def harvest_bytes_from_bytearray(o):
    raise NotImplemented()

def harvest_complex_from_bytearray(o):
    raise NotImplemented()

def harvest_dict_from_bytearray(o):
    raise NotImplemented()

def harvest_float_from_bytearray(o):
    raise NotImplemented()

def harvest_int_from_bytearray(o):
    raise NotImplemented()

@flipped
def harvest_list_from_bytearray(o):
    for x in range(-1, 2):
        yield [i+x for i in o]
        yield [(i+x)%2 for i in o]
        yield [i+x for i in o if i%2]
        yield [i+x for i in o if not i%2]

def harvest_set_from_bytearray(o):
    yield from map(set, harvest_list_from_bytearray(o))

def harvest_str_from_bytearray(o):
    for l in harvest_list_from_bytearray(o):
        with suppress(Exception):
            yield ''.join(map(chr, l))

def harvest_tuple_from_bytearray(o):
    yield from map(tuple, harvest_list_from_bytearray(o))

def harvest_bool_from_bytes(o):
    for i in o:
        yield from (x=='1' for x in bin(i)[2:])

def harvest_bytearray_from_bytes(o):
    raise NotImplemented()

def harvest_bytes_from_bytes(o):
    raise NotImplemented()

def harvest_complex_from_bytes(o):
    raise NotImplemented()

def harvest_dict_from_bytes(o):
    raise NotImplemented()

def harvest_float_from_bytes(o):
    raise NotImplemented()

def harvest_int_from_bytes(o):
    for i in o:
        yield from harvest_int_from_int(i)

@flipped
def harvest_list_from_bytes(o):
    yield [i for i in o]
    yield [bool(i) for i in o]
    yield [str(i) for i in o]
    yield [float(i) for i in o]

def harvest_set_from_bytes(o):
    yield from map(set, harvest_list_from_bytes(o))

def harvest_str_from_bytes(o):
    raise NotImplemented()

def harvest_tuple_from_bytes(o):
    yield from map(tuple, harvest_list_from_bytes(o))

def harvest_bool_from_complex(o):
    raise NotImplemented()

def harvest_bytearray_from_complex(o):
    raise NotImplemented()

def harvest_bytes_from_complex(o):
    raise NotImplemented()

def harvest_complex_from_complex(o):
    raise NotImplemented()

def harvest_dict_from_complex(o):
    raise NotImplemented()

def harvest_float_from_complex(o):
    raise NotImplemented()

def harvest_int_from_complex(o):
    raise NotImplemented()

@flipped
def harvest_list_from_complex(o):
    raise NotImplemented()

def harvest_set_from_complex(o):
    raise NotImplemented()

def harvest_str_from_complex(o):
    raise NotImplemented()

def harvest_tuple_from_complex(o):
    raise NotImplemented()

def harvest_bool_from_dict(o):
    raise NotImplemented()

def harvest_bytearray_from_dict(o):
    raise NotImplemented()

def harvest_bytes_from_dict(o):
    raise NotImplemented()

def harvest_complex_from_dict(o):
    raise NotImplemented()

def harvest_dict_from_dict(o):
    raise NotImplemented()

def harvest_float_from_dict(o):
    raise NotImplemented()

def harvest_int_from_dict(o):
    raise NotImplemented()

@flipped
def harvest_list_from_dict(o):
    raise NotImplemented()

def harvest_set_from_dict(o):
    raise NotImplemented()

def harvest_str_from_dict(o):
    raise NotImplemented()

def harvest_tuple_from_dict(o):
    raise NotImplemented()

def harvest_bool_from_float(o):
    raise NotImplemented()

def harvest_bytearray_from_float(o):
    raise NotImplemented()

def harvest_bytes_from_float(o):
    raise NotImplemented()

def harvest_complex_from_float(o):
    raise NotImplemented()

def harvest_dict_from_float(o):
    raise NotImplemented()

def harvest_float_from_float(o):
    raise NotImplemented()

def harvest_int_from_float(o):
    raise NotImplemented()

@flipped
def harvest_list_from_float(o):
    raise NotImplemented()

def harvest_set_from_float(o):
    raise NotImplemented()

def harvest_str_from_float(o):
    raise NotImplemented()

def harvest_tuple_from_float(o):
    raise NotImplemented()

def harvest_bool_from_int(o):
    yield o % 2 == 1
    yield o % 2 == 0
    yield from (x=='1' for x in bin(i))
    yield from (x=='1' for x in bin(i**2))

def harvest_bytearray_from_int(o):
    raise NotImplemented()

def harvest_bytes_from_int(o):
    raise NotImplemented()

def harvest_complex_from_int(o):
    raise NotImplemented()

def harvest_dict_from_int(o):
    raise NotImplemented()

def harvest_float_from_int(o):
    raise NotImplemented()

def harvest_int_from_int(o):
    yield from (i+x for x in range(-10, 11))
    yield from (i//x for x in range(-10, -1))
    yield from (i//x for x in range(1, 11))
    yield from (int(i*x) for x in range(-10, 11))
    yield from (i%x for x in range(-10, -1))
    yield from (i%x for x in range(1, 11))

@flipped
def harvest_list_from_int(o):
    bin_o = bin(o)[2:]
    yield list(bin_o)
    as_bools = [i=='1' for i in bin_o]
    for i in range(1, len(as_bools)):
        yield as_bools[:i]
        yield as_bools[i:]
        yield [(not x) for x in as_bools[:i]]
        yield [(not x) for x in as_bools[i:]]

def harvest_set_from_int(o):
    yield from map(set, harvest_list_from_int(o))

def harvest_str_from_int(o):
    yield bin(i)
    yield json.dumps(i)
    chars = filter(bool, map_attempt(lambda i:(printables[i%len(printables)]), harvest_int_from_int(o)))
    for l in kinda_random_small_int:
        out = ''.join(c for _,c in zip(range(l), chars))
        if out:
            yield out
        else:
            break

def harvest_tuple_from_int(o):
    for i in harvest_list_from_int(o):
        yield tuple(i)
        yield tuple(set(i))

def harvest_bool_from_list(o):
    as_bools = list(map(bool, o))
    yield from as_bools
    for i in as_bools:
        yield not i

def harvest_bytearray_from_list(o):
    yield from map(bytearray, harvest_bytes_from_list(o))

def harvest_bytes_from_list(o):
    yield from map_attempt(str_encode_or_ignore, harvest_str_from_list(o))

def harvest_complex_from_list(o):
    raise NotImplemented()

def harvest_dict_from_list(o):
    len_o = len(o)
    o = itertools.cycle(o)
    for i in range(1, int(len_o*2)):
        with suppress(Exception):
            yield {next(o):next(o) for _ in range(i)}

def harvest_float_from_list(o):
    pipe = iter(harvest_int_from_list(o))
    for a, b in zip(pipe, pipe):
        yield a * b
        if b and a:
            yield a/b
            yield b/a

def harvest_int_from_list(o):
    yield len(o)
    for fn in [len, int, ord]:
        yield from map_attempt(fn, o)
    yield from str_encode_or_ignore(repr(o))

@flipped
def harvest_list_from_list(o):
    yield o
    if o:
        for i in range(1, int(math.sqrt(len(o)))+1):
            yield [v for ii,v in enumerate(o) if not ii%i]
            yield [v for ii,v in enumerate(o) if ii%i]
        yield [i for i in o if i]
        yield [i for i in o if not i]

def harvest_set_from_list(o):
    for l in harvest_list_from_list(o):
        yield {i for i in l if hashable(i)}

def harvest_str_from_list(o):
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
    yield from map(tuple, harvest_list_from_list(o))
    yield from map(tuple, harvest_set_from_list(o))

def harvest_bool_from_set(o):
    raise NotImplemented()

def harvest_bytearray_from_set(o):
    raise NotImplemented()

def harvest_bytes_from_set(o):
    raise NotImplemented()

def harvest_complex_from_set(o):
    raise NotImplemented()

def harvest_dict_from_set(o):
    raise NotImplemented()

def harvest_float_from_set(o):
    raise NotImplemented()

def harvest_int_from_set(o):
    raise NotImplemented()

@flipped
def harvest_list_from_set(o):
    raise NotImplemented()

def harvest_set_from_set(o):
    raise NotImplemented()

def harvest_str_from_set(o):
    raise NotImplemented()

def harvest_tuple_from_set(o):
    raise NotImplemented()

def harvest_bool_from_str(o):
    raise NotImplemented()

def harvest_bytearray_from_str(o):
    raise NotImplemented()

def harvest_bytes_from_str(o):
    raise NotImplemented()

def harvest_complex_from_str(o):
    raise NotImplemented()

def harvest_dict_from_str(o):
    raise NotImplemented()

def harvest_float_from_str(o):
    raise NotImplemented()

def harvest_int_from_str(o):
    raise NotImplemented()

@flipped
def harvest_list_from_str(o):
    raise NotImplemented()

def harvest_set_from_str(o):
    raise NotImplemented()

def harvest_str_from_str(o):
    yield o.upper()
    yield o.lower()
    yield o.strip()
    common_chars = ['\n', '"', "'", ' ', '\t', '.', ',', ':']
    yield from (o.replace(old_char, new_char) for old_char, new_char in itertools.combinations(common_chars, 2) if old_char in o)
    yield ''.join(x for x in o if x.isnumeric())
    yield ''.join(x for x in o if not x.isnumeric())

def harvest_tuple_from_str(o):
    raise NotImplemented()

def harvest_bool_from_tuple(o):
    yield from map(bool, o)

def harvest_bytearray_from_tuple(o):
    raise NotImplemented()

def harvest_bytes_from_tuple(o):
    raise NotImplemented()

def harvest_complex_from_tuple(o):
    raise NotImplemented()

def harvest_dict_from_tuple(o):
    raise NotImplemented()

def harvest_float_from_tuple(o):
    yield from harvest_float_from_list(list(o))

def harvest_int_from_tuple(o):
    yield from harvest_int_from_list(list(o))

@flipped
def harvest_list_from_tuple(o):
    raise NotImplemented()

def harvest_set_from_tuple(o):
    raise NotImplemented()

def harvest_str_from_tuple(o):
    raise NotImplemented()

def harvest_tuple_from_tuple(o):
    raise NotImplemented()


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

def mutate(o, output_type):
    ''' this function takes an input object and runs mutations on it to harvest
        inputs of the specified output type. this allows battle_tested to create
        more test inputs without needing to rely on random generation '''
    global mutation_map

    if isinstance(o, output_type):
        for i in mutation_map[type(o), output_type](o):
            yield i
    else:
        for i in mutation_map[type(o), output_type](o):
            yield i
            yield from mutation_map[type(i), output_type](i)

if __name__ == '__main__':
    for test in ['hi', 5]:
        for i,v in enumerate(mutate(test, str)):
            print(repr(v))

