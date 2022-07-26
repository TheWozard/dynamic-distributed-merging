from dataclasses import dataclass
from typing import Dict, List
import unittest

from src.merge import merge


@dataclass
class TestCase:
    name: str
    input: List[Dict]
    expected: Dict


class TestMerge(unittest.TestCase):

    def test_basic_merge(self):
        cases = [
            TestCase(name='empty_dicts', input=[{}, {}], expected={}),
            TestCase(name='simple_merge', input=[{"A": "a"}, {
                     "B": "b"}], expected={"A": "a", "B": "b"}),
            TestCase(name='overlapping_merge', input=[{"A": "a"}, {
                     "A": "b"}], expected={"A": "a"}),
            TestCase(name='recursive_object_merge', input=[{"A": "a", "B": {"C": "c"}}, {
                "A": "b", "B": {"D": "d"}}], expected={"A": "a", "B": {"C": "c", "D": "d"}}),
        ]

        for case in cases:
            actual = merge(*case.input)
            self.assertDictEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )


if __name__ == '__main__':
    unittest.main()
