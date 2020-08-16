from unittest import TestCase, main


def input_type_combos(user_settings, arg_count):
    assert isinstance(user_settings, (list, tuple, set)), user_settings

    user_settings = user_settings if isinstance(
        user_settings, tuple) else tuple(user_settings)

    raise NotImplemented("havent gotten to this one yet")


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
        with self.assertRaises(UsageError):
            set(input_type_combos((int, float, (str, bool)), 1))

    def test_not_enough_args_for_types(self):
        with self.assertRaises(UsageError):
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
