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
            TestCase(name='empty_dicts', input=[{}, {}], expected={})
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
