import unittest
from dataclasses import dataclass
from typing import Dict, List

from src.context import DictMergeContext, ListMergeContext, MergeContext
from src.nodes import INode, data_to_node, merge


class TestMerge(unittest.TestCase):

    def test_merge(self):
        @dataclass
        class TestCase:
            name: str
            input: List[INode]
            expected: Dict

        cases = [
            # Basic Dictionary Merge Cases
            TestCase(name='empty_dicts_are_removed', input=[
                data_to_node(MergeContext(), {}),
            ], expected=None),
            TestCase(name='empty_dicts_are_not_removed_when_allow_empty', input=[
                data_to_node(MergeContext(allow_empty=True), {}),
            ], expected={}),
            TestCase(name='empty_dicts_are_still_removed_when_lower_priority_is_allow_empty', input=[
                data_to_node(MergeContext(priority=1), {}),
                data_to_node(MergeContext(allow_empty=True), {}),
            ], expected=None),
            TestCase(name='empty_dicts_are_removed_deeply', input=[
                data_to_node(MergeContext(), {'A': {'B': {}}}),
            ], expected=None),
            TestCase(name='empty_dicts_are_not_removed_when_allow_empty_even_for_children', input=[
                data_to_node(MergeContext(allow_empty=True), {'A': {'B': {}}}),
            ], expected={'A': {'B': {}}}),
            TestCase(name='empty_values_in_dicts_are_ignored', input=[
                data_to_node(MergeContext(), {'A': None}),
            ], expected=None),
            TestCase(name='empty_values_in_dicts_are_allowed_in_dict', input=[
                data_to_node(MergeContext(allow_none=True), {'A': None}),
            ], expected={'A': None}),

            # Basic List Merge Cases
            TestCase(name='empty_lists_are_removed', input=[
                data_to_node(MergeContext(), []),
            ], expected=None),
            TestCase(name='empty_lists_are_not_removed_when_allow_empty', input=[
                data_to_node(MergeContext(allow_empty=True), []),
            ], expected=[]),
            TestCase(name='empty_lists_are_still_removed_when_lower_priority_is_allow_empty', input=[
                data_to_node(MergeContext(priority=1), []),
                data_to_node(MergeContext(allow_empty=True), []),
            ], expected=None),
            TestCase(name='empty_lists_are_removed_deeply', input=[
                data_to_node(MergeContext(), [[[], []]]),
            ], expected=None),
            TestCase(name='empty_lists_are_not_removed_when_allow_empty_even_for_children', input=[
                data_to_node(MergeContext(allow_empty=True), [[[], []]]),
            ], expected=[[[], []]]),
            TestCase(name='empty_values_in_lists_are_ignored', input=[
                data_to_node(MergeContext(), [None]),
            ], expected=None),
            TestCase(name='empty_values_in_lists_are_allowed_in_dict', input=[
                data_to_node(MergeContext(allow_none=True), [None]),
            ], expected=[None]),

            # Basic Value Merge Cases
            TestCase(name='empty_values_are_skipped_in_value', input=[
                data_to_node(MergeContext(priority=1), None),
                data_to_node(MergeContext(), 'Success'),
            ], expected='Success'),
            TestCase(name='empty_values_are_kept_in_value_when_allow_none', input=[
                data_to_node(MergeContext(priority=1, allow_none=True), None),
                data_to_node(MergeContext(), 'Failure'),
            ], expected=None),
            TestCase(name='empty_values_are_kept_in_value_when_allow_none_even_if_it_is_a_lower_priority', input=[
                data_to_node(MergeContext(priority=2), None),
                data_to_node(MergeContext(priority=1, allow_none=True), None),
                data_to_node(MergeContext(), 'Failure'),
            ], expected=None),
            TestCase(name='terminal_does_not_apply_to_values', input=[
                data_to_node(MergeContext(priority=1, terminal=True), None),
                data_to_node(MergeContext(), 'Success'),
            ], expected='Success'),

            # # Ordering Cases
            TestCase(name='order_is_based_on_priority_highest_first', input=[
                data_to_node(MergeContext(), 'Second'),
                data_to_node(MergeContext(priority=1), 'First'),
            ], expected='First'),
            TestCase(name='order_is_based_on_order_lowest_first', input=[
                data_to_node(MergeContext(order=1), 'Second'),
                data_to_node(MergeContext(), 'First'),
            ], expected='First'),

            # Basic Data Merge Cases
            TestCase(name='merge_dicts', input=[
                data_to_node(MergeContext(priority=1), {'A': 'a'}),
                data_to_node(MergeContext(), {'B': 1}),
            ], expected={'A': 'a', 'B': 1}),
            TestCase(name='merge_dicts_identical_key', input=[
                data_to_node(MergeContext(priority=1), {'A': 'Success'}),
                data_to_node(MergeContext(), {'A': 'Failure'}),
            ], expected={'A': 'Success'}),
            TestCase(name='merge_dicts_identical_key_skips_none', input=[
                data_to_node(MergeContext(priority=1), {'A': None}),
                data_to_node(MergeContext(), {'A': 'Success'}),
            ], expected={'A': 'Success'}),
            TestCase(name='merge_dicts_identical_key_does_not_skips_none_with_allow_none', input=[
                data_to_node(MergeContext(priority=1, allow_none=True), {'A': None}),
                data_to_node(MergeContext(), {'A': 'Success'}),
            ], expected={'A': None}),

            # Deep Merge Cases
            TestCase(name='merge_dicts_identical_key', input=[
                data_to_node(MergeContext(priority=1), {'song': {'title': 'walk of life'}}),
                data_to_node(MergeContext(), {'song': {'author': 'dire straits', 'title': 'unknown'}}),
            ], expected={'song': {'title': 'walk of life', 'author': 'dire straits'}}),

            # Advanced Merge Cases
            TestCase(name='control_document', input=[
                data_to_node(MergeContext(priority=1, terminal=True), {
                    'author': {'name': None}, 'songs': [{'$id': 'im_okay', 'title': None}], 'most_popular': None
                }),
                data_to_node(MergeContext(),  {
                    'author': {'slug': 'honest_men', 'name': 'Honest Men', 'year_formed': 2015},
                    'songs': [
                        {'$id': 'im_okay', 'title': 'Im Okay', 'length': 251},
                        {'$id': 'aint_no_mountain_high_enough', 'title': 'Aint No Mountain High Enough', 'length': 280}],
                    'most_popular': 'im_okay'
                }),
            ], expected={
                'author': {'name': 'Honest Men'}, 'songs': [{'title': 'Im Okay'}], 'most_popular': 'im_okay'
            }),
            TestCase(name='data_suppression', input=[
                data_to_node(DictMergeContext(priority=1, nodes={
                    'privileged': MergeContext(terminal=True),
                    'weather': DictMergeContext(nodes={
                        'chance_of_meatballs': MergeContext(allow_none=True)
                    }),
                    'danger_zones': ListMergeContext(default=MergeContext(allow_none=True)),
                }), None),
                data_to_node(MergeContext(), {
                    'privileged': {'secret': 'sky is blue'},
                    'weather': {'overview': 'sunny', 'chance_of_meatballs': 0.5},
                    'danger_zones': ['swallow falls'],
                }),
            ], expected={'weather': {'overview': 'sunny'}}),
            TestCase(name='data_suppression_with_allow_none_show_expected_nodes', input=[
                data_to_node(DictMergeContext(priority=1, nodes={
                    'privileged': MergeContext(terminal=True),
                    'weather': DictMergeContext(nodes={
                        'chance_of_meatballs': MergeContext(allow_none=True)
                    }),
                    'danger_zones': ListMergeContext(default=MergeContext(allow_none=True)),
                }), None),
                data_to_node(MergeContext(allow_none=True),  {
                    'privileged': {'secret': 'sky is blue'},
                    'weather': {'overview': 'sunny', 'chance_of_meatballs': 0.5},
                    'danger_zones': ['swallow falls'],
                }),
            ], expected={
                'privileged': None,
                'weather': {'overview': 'sunny', 'chance_of_meatballs': None},
                'danger_zones': [None],
            }),
            TestCase(name='data_suppression_with_allow_empty_show_empty_objects', input=[
                data_to_node(DictMergeContext(priority=1, nodes={
                    'privileged': MergeContext(terminal=True),
                    'weather': DictMergeContext(nodes={
                        'chance_of_meatballs': MergeContext(allow_none=True)
                    }),
                    'danger_zones': ListMergeContext(default=MergeContext(allow_none=True)),
                }), None),
                data_to_node(MergeContext(allow_empty=True),  {
                    'privileged': {'secret': 'sky is blue'},
                    'weather': {'overview': 'sunny', 'chance_of_meatballs': 0.5},
                    'danger_zones': ['swallow falls'],
                }),
            ], expected={'privileged': {}, 'weather': {'overview': 'sunny'}, 'danger_zones': []}),
        ]

        for case in cases:
            actual = merge(case.input)
            self.assertEqual(
                case.expected,
                actual,
                f'failed test {case.name} expected {case.expected}, actual {actual}',
            )


if __name__ == '__main__':
    unittest.main()
