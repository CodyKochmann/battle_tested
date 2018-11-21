import itertools

def transform_bool(o, output_type):
    if output_type is bool:
        yield bool(o)
        yield not bool(o)

def transform_str(i, output_type):
    if output_type is str:
        yield i.upper()
        yield i.lower()
        yield i.strip()
        common_chars = ['\n', '"', "'", ' ', '\t', '.', ',', ':']
        yield from (i.replace(old_char, new_char) for old_char, new_char in itertools.combinations(common_chars, 2) if old_char in i)
        yield ''.join(x for x in i if x.isnumeric())
        yield ''.join(x for x in i if not x.isnumeric())
        
def transform_int(i, output_type):
    if output_type is int:
        yield from (i+x for x in range(-10, 11))
        yield from (i//x for x in range(-10, -1))
        yield from (i//x for x in range(1, 11))
        yield from (int(i*x) for x in range(-10, 11))
        yield from (i%x for x in range(-10, -1))
        yield from (i%x for x in range(1, 11))
    elif output_type is bool:
        yield from transform_bool(i, bool)
        yield from (x=='1' for x in bin(i))
        yield from (x=='1' for x in bin(i**2))
    elif output_type is str:
        yield from transform_str(bin(i), str)


def mutator(input_variable, output_type):
    if type(input_variable) is int:
        yield from transform_int(input_variable, output_type)
    # step 1 do common mutations to the input_variable

    # step 2 map those mutations to the output type

if __name__ == '__main__':
    print(list(mutator(5, bool)))
    print(list(mutator(5, int)))
    print(list(mutator(5, str)))