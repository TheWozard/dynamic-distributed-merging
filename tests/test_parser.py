import unittest
from dataclasses import dataclass
from typing import List

from src.nodes import merge
from src.parser import parse_context


class TestMerge(unittest.TestCase):

    def test_parse_merge(self):
        @dataclass
        class TestCase:
            name: str
            _input: List[any]
            expected: any

        cases = [
            # Basic Dictionary Merge Cases
            TestCase(name='empty_dicts_are_removed', _input=[{}, {}], expected=None),
            TestCase(name='empty_dicts_are_not_removed_when_allow_empty', _input=[{'$allow_empty': True}], expected={}),
            TestCase(name='empty_dicts_are_still_removed_when_lower_priority_is_allow_empty',
                     _input=[{'$priority': 1}, {'$allow_empty': True}], expected=None),
        ]

        for case in cases:
            actual = merge([parse_context(_input) for _input in case._input])
            self.assertEqual(
                case.expected,
                actual,
                f'failed test {case.name} expected {case.expected}, actual {actual}',
            )


if __name__ == '__main__':
    unittest.main()
