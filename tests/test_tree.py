import unittest
from dataclasses import dataclass
from typing import Optional

from src.tree import MostRecentTree


class TestContext(unittest.TestCase):

    def test_tree_get_node(self):
        @dataclass
        class TestCase:
            name: str
            tree: MostRecentTree[str]
            node: str
            expected: Optional[MostRecentTree[str]]

        extra_nodes = {'Extra': MostRecentTree(data='too_far', nodes={})}

        cases = [
            TestCase(
                name='missing_node',
                tree=MostRecentTree(data='root'),
                node='missing', expected=None
            ),
            TestCase(
                name='edge_node',
                tree=MostRecentTree(nodes={
                    'A': MostRecentTree(data='expected')
                }), node='A', expected=MostRecentTree(data='expected', nodes={})
            ),
            TestCase(
                name='middle_node',
                tree=MostRecentTree(nodes={
                    'A': MostRecentTree(data='expected', nodes=extra_nodes)
                }), node='A', expected=MostRecentTree(data='expected', nodes=extra_nodes)
            ),
            TestCase(
                name='middle_node_no_data',
                tree=MostRecentTree(nodes={
                    'A': MostRecentTree(nodes=extra_nodes)
                }), node='A', expected=MostRecentTree(nodes=extra_nodes)
            ),
            TestCase(
                name='middle_node_recent_data',
                tree=MostRecentTree(data='fallthrough', nodes={
                    'A': MostRecentTree(nodes=extra_nodes)
                }), node='A', expected=MostRecentTree(data='fallthrough', nodes=extra_nodes)
            ),
            TestCase(
                name='bad_middle_node_recent_data',
                tree=MostRecentTree(data='fallthrough', nodes={
                    'A': MostRecentTree(nodes=extra_nodes)
                }), node='B', expected=None
            ),
        ]

        for case in cases:
            actual = case.tree.get_node(case.node)
            self.assertEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )

    def test_tree_get_node_default(self):
        @dataclass
        class TestCase:
            name: str
            tree: MostRecentTree[str]
            node: str
            default: str
            expected: Optional[MostRecentTree[str]]

        extra_nodes = {'Extra': MostRecentTree(data='too_far', nodes={})}

        cases = [
            TestCase(
                name='missing_node',
                tree=MostRecentTree(data='root'),
                node='missing', default='default', expected=MostRecentTree(data='default', nodes={})
            ),
            TestCase(
                name='edge_node',
                tree=MostRecentTree(nodes={
                    'A': MostRecentTree(data='expected')
                }), node='A', default='default', expected=MostRecentTree(data='expected', nodes={})
            ),
            TestCase(
                name='bad_middle_node_recent_data',
                tree=MostRecentTree(data='fallthrough', nodes={
                    'A': MostRecentTree(nodes=extra_nodes)
                }), node='B', default='default', expected=MostRecentTree(data='default', nodes={})
            ),
        ]

        for case in cases:
            actual = case.tree.get_node_default(case.node, case.default)
            self.assertEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )

    def test_tree_get_or_persist(self):
        @dataclass
        class TestCase:
            name: str
            tree: MostRecentTree[str]
            node: str
            expected: Optional[MostRecentTree[str]]

        extra_nodes = {'Extra': MostRecentTree(data='too_far', nodes={})}

        cases = [
            TestCase(
                name='missing_node',
                tree=MostRecentTree(data='root'),
                node='missing', expected=MostRecentTree(data='root', nodes={})
            ),
            TestCase(
                name='bad_middle_node_recent_data',
                tree=MostRecentTree(data='fallthrough', nodes={
                    'A': MostRecentTree(nodes=extra_nodes)
                }), node='B', expected=MostRecentTree(data='fallthrough', nodes={})
            ),
        ]

        for case in cases:
            actual = case.tree.get_or_persist(case.node)
            self.assertEqual(
                case.expected,
                actual,
                f"failed test {case.name} expected {case.expected}, actual {actual}",
            )


if __name__ == '__main__':
    unittest.main()
