from itertools import product
from unittest import TestCase, main


def has_nested_combos(input_types):
    ''' returns True if any object in the type collection is not a type '''
    assert isinstance(input_types, (list, tuple, set)), input_types
    return any(not isinstance(i, type) for i in input_types)


def flatten_types(input_types):
    ''' returns every type from a nested structure '''
    assert isinstance(input_types, (list, tuple, set, type)), input_types
    if isinstance(input_types, type):
        yield input_types
    else:
        for i in input_types:
            yield from flatten_types(i)


class IllegalTypeComboSettings(ValueError):
    '''raised if illegal combination of type_combos are entered with a give arg_count'''


def type_combos(input_types, arg_count):
    ''' expands all combinations generated from the user's given settings '''
    assert isinstance(input_types, (list, tuple, set)), input_types
    assert isinstance(arg_count, int), arg_count
    assert arg_count > 0, arg_count
    if arg_count == 1:
        # flatten out the types and yield the unique product
        yield from product(set(flatten_types(input_types)))
    elif has_nested_combos(input_types):
        if len(input_types) == arg_count:
            # turn every input type into a tuple
            pipe = (
                (i,) if isinstance(i, type) else i
                for i in input_types
            )
            # yield out the product of those tuples
            yield from product(*pipe)
        else:
            raise IllegalTypeComboSettings(f'{locals()}')
    else:
        # yield out the product of every type for each arg
        yield from product(input_types, repeat=arg_count)


class Test_input_type_combos(TestCase):
    def test_basic_one_type_one_arg(self):
        self.assertEqual(set(input_type_combos((int, ), 1)), {(int, )})

    def test_basic_two_types_one_arg(self):
        self.assertEqual(set(input_type_combos((int, bool), 1)),
                         {(int, )(bool, )})

    def test_basic_one_type_two_args(self):
        self.assertEqual(set(input_type_combos((int, ), 2)), {(int, int)})

    def test_basic_two_types_two_args(self):
        self.assertEqual(set(input_type_combos((int, bool), 2)), {(int, bool)})

    def test_one_nested_two_args(self):
        self.assertEqual(set(input_type_combos((int, (bool, str)), 2)),
                         {(int, bool), (int, str)})

    def test_two_nested_three_args(self):
        self.assertEqual(
            set(input_type_combos(((int, float), bool, (bool, str)), 2)), {
                (float, bool, bool),
                (float, bool, str),
                (int, bool, bool),
                (int, bool, str)
            })

    def test_two_nested_three_args_different_sizes(self):
        self.assertEqual(
            set(input_type_combos(((int, float), bool, (bool, str, int)), 2)),
            {
                (float, bool, bool),
                (float, bool, str),
                (float, bool, str),
                (int, bool, bool),
                (int, bool, str),
                (int, bool, str)
            })

    def test_three_nested_three_args_different_sizes(self):
        self.assertEqual(
            set(
                input_type_combos(
                    ((int, float), (bool, int), (bool, str, int)), 2)), {
                        (float, bool, bool),
                        (float, bool, str),
                        (float, bool, str),
                        (float, int, bool),
                        (float, int, str),
                        (float, int, str),
                        (int, bool, bool),
                        (int, bool, str),
                        (int, bool, str),
                        (int, int, bool),
                        (int, int, str),
                        (int, int, str)
                    })

    def test_no_nested_single_combos(self):
        with self.assertRaises(ValueError):
            set(input_type_combos((int, float, (str, bool)), 1))

    def test_not_enough_args_for_types(self):
        with self.assertRaises(ValueError):
            set(
                input_type_combos(
                    (
                        int,
                        float,
                        (
                            str, bool
                        )  # no nested cases here since everything will apply to every arg when types outnumbers args
                    ),
                    2))

    def test_multiply_types_for_not_enough_args(self):
        self.assertEqual(
            set(input_type_combos((
                int,
                float,
                str
            ), 2)), {(int, int), (int, float), (int, str), (float, int),
                     (float, float), (float, str), (str, int), (str, float),
                     (str, str)})


if __name__ == '__main__':
    main(verbosity=2)
