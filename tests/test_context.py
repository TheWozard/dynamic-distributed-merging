import unittest
from dataclasses import dataclass
from typing import List

from src.context import MergeContext


class TestMergeContext(unittest.TestCase):

    def test_get_sort_key(self):
        @dataclass
        class TestCase:
            name: str
            input: List[MergeContext]
            expected: List[MergeContext]

        cases = [
            TestCase(name='empty_dicts', input=[], expected=[]),
            TestCase(name='single_doc', input=[
                MergeContext(priority=0, order=0),
            ], expected=[
                MergeContext(priority=0, order=0),
            ]),
            TestCase(name='priority', input=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=0, order=0),
            ], expected=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=0, order=0),
            ]),
            TestCase(name='order', input=[
                MergeContext(priority=0, order=0),
                MergeContext(priority=0, order=1),
            ], expected=[
                MergeContext(priority=0, order=0),
                MergeContext(priority=0, order=1),
            ]),
            TestCase(name='in_order', input=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=1, order=1),
                MergeContext(priority=0, order=2),
                MergeContext(priority=0, order=3),
            ], expected=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=1, order=1),
                MergeContext(priority=0, order=2),
                MergeContext(priority=0, order=3),
            ]),
            TestCase(name='mixed', input=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=0, order=1),
                MergeContext(priority=1, order=2),
                MergeContext(priority=0, order=3),
                MergeContext(priority=2, order=4),
                MergeContext(priority=-1, order=5),
            ], expected=[
                MergeContext(priority=2, order=4),
                MergeContext(priority=1, order=0),
                MergeContext(priority=1, order=2),
                MergeContext(priority=0, order=1),
                MergeContext(priority=0, order=3),
                MergeContext(priority=-1, order=5),
            ]),
            TestCase(name='empty_is_treated_as_0_0', input=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=0, order=1),
                MergeContext(priority=1, order=1),
                MergeContext(priority=-1, order=0),
                MergeContext(priority=0, order=-1),
                MergeContext(priority=-1, order=-1),
                MergeContext(),
            ], expected=[
                MergeContext(priority=1, order=0),
                MergeContext(priority=1, order=1),
                MergeContext(priority=0, order=-1),
                MergeContext(),
                MergeContext(priority=0, order=1),
                MergeContext(priority=-1, order=-1),
                MergeContext(priority=-1, order=0),
            ]),
        ]

        for case in cases:
            actual = sorted(case.input, key=MergeContext.get_sort_key)
            self.assertListEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )

    def test_merge_in(self):
        @dataclass
        class TestCase:
            name: str
            original: MergeContext
            merge: MergeContext
            expected: MergeContext

        cases = [
            TestCase(
                name='empty+empty=empty',
                original=MergeContext(),
                merge=MergeContext(),
                expected=MergeContext(),
            ),
            TestCase(
                name='can_updated_all_params',
                original=MergeContext(),
                merge=MergeContext(priority=1, order=1, terminal=True, allow_none=True, allow_empty=True),
                expected=MergeContext(priority=1, order=1, terminal=True, allow_none=True, allow_empty=True),
            ),
            TestCase(
                name='wont_update_any_params_that_are_already_set',
                original=MergeContext(priority=0, order=0, terminal=False, allow_none=False, allow_empty=False),
                merge=MergeContext(priority=1, order=1, terminal=True, allow_none=True, allow_empty=True),
                expected=MergeContext(priority=0, order=0, terminal=False, allow_none=False, allow_empty=False),
            ),
        ]

        for case in cases:
            self.assertEqual(
                case.expected,
                case.original.update(case.merge),
                f"failed test {case.name} expected {case.expected}, actual {case.original}",
            )


if __name__ == '__main__':
    unittest.main()
