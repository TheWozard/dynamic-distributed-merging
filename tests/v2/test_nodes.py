from dataclasses import dataclass
from typing import Dict, List
import unittest

from src.v2.nodes import data_to_node, merge


class TestMerge(unittest.TestCase):

    def test_no_context_merge(self):
        @dataclass
        class TestCase:
            name: str
            input: List[Dict]
            expected: Dict

        cases = [
            TestCase(name='empty_dicts', input=[{}, {}], expected={}),
            TestCase(name='simple_merge', input=[{"A": "a"}, {
                     "B": "b"}], expected={"A": "a", "B": "b"}),
            TestCase(name='overlapping_merge', input=[{"A": "a"}, {
                     "A": "b"}], expected={"A": "a"}),
            TestCase(name='objects', input=[{"A": {}}, {
                     "B": {}}], expected={"A": {}, "B": {}}),
            TestCase(name='recursive_object_merge', input=[{"A": "a", "B": {"C": "c"}}, {
                "A": "b", "B": {"D": "d"}}], expected={"A": "a", "B": {"C": "c", "D": "d"}}),
            TestCase(name='$_is_ignored', input=[
                     {"A": "a", "$ignore": "data"}], expected={"A": "a"}),
            TestCase(name='list_of_strings', input=[
                     {"A": ['a', 'à', 'á']}, {"A": ['â']}], expected={"A": ['a', 'à', 'á', 'â']}),
            TestCase(name='mixed_list', input=[
                     {"A": [{'C': 'c'}, [3], 1, 'a']}, {"A": [{'D': 'd'}, [4], 2, 'b']}], expected={"A": [{'C': 'c'}, [3], 1, 'a', {'D': 'd'}, [4], 2, 'b']}),
            TestCase(name='list_ids', input=[
                     {"A": [{'$id': '1', 'A': 'a'}]}, {"A": [{'$id': '1', 'B': 'b'}]}], expected={"A": [{'A': 'a', 'B': 'b'}]}),
        ]

        for case in cases:
            actual = merge([data_to_node(data) for data in case.input])
            self.assertDictEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )


if __name__ == '__main__':
    unittest.main()
