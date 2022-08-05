import unittest
from dataclasses import dataclass
from typing import List

from src.v2.context import MergeContext


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
        ]

        for case in cases:
            case.original.merge_in(case.merge)
            self.assertEqual(
                case.expected,
                case.original,
                f"failed test {case.name} expected {case.expected}, actual {case.original}",
            )


if __name__ == '__main__':
    unittest.main()
