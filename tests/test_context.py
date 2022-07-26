import unittest
from dataclasses import dataclass
from typing import List

from src.context import MergeContext, MergeDocument


def simple_doc(priority=0, order=0) -> MergeDocument:
    return MergeDocument(context=MergeContext(
        priority=priority, order=order), document={})


class TestContext(unittest.TestCase):

    def test_document_sort(self):
        @dataclass
        class TestCase:
            name: str
            input: List[MergeDocument]
            expected: List[MergeDocument]

        cases = [
            TestCase(name='empty_dicts', input=[], expected=[]),
            TestCase(name='single_doc', input=[
                simple_doc(priority=0, order=0),
            ], expected=[
                simple_doc(priority=0, order=0),
            ]),
            TestCase(name='priority', input=[
                simple_doc(priority=1, order=0),
                simple_doc(priority=0, order=0),
            ], expected=[
                simple_doc(priority=1, order=0),
                simple_doc(priority=0, order=0),
            ]),
            TestCase(name='order', input=[
                simple_doc(priority=0, order=0),
                simple_doc(priority=0, order=1),
            ], expected=[
                simple_doc(priority=0, order=0),
                simple_doc(priority=0, order=1),
            ]),
            TestCase(name='in_order', input=[
                simple_doc(priority=1, order=0),
                simple_doc(priority=1, order=1),
                simple_doc(priority=0, order=2),
                simple_doc(priority=0, order=3),
            ], expected=[
                simple_doc(priority=1, order=0),
                simple_doc(priority=1, order=1),
                simple_doc(priority=0, order=2),
                simple_doc(priority=0, order=3),
            ]),
            TestCase(name='mixed', input=[
                simple_doc(priority=1, order=0),
                simple_doc(priority=0, order=1),
                simple_doc(priority=1, order=2),
                simple_doc(priority=0, order=3),
                simple_doc(priority=2, order=4),
                simple_doc(priority=-1, order=5),
            ], expected=[
                simple_doc(priority=2, order=4),
                simple_doc(priority=1, order=0),
                simple_doc(priority=1, order=2),
                simple_doc(priority=0, order=1),
                simple_doc(priority=0, order=3),
                simple_doc(priority=-1, order=5),
            ]),
        ]

        for case in cases:
            actual = sorted(case.input, key=MergeDocument.get_sort_key)
            self.assertListEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )


if __name__ == '__main__':
    unittest.main()
