from dataclasses import dataclass, field
from typing import Dict, Generic, Optional, Tuple, TypeVar

T = TypeVar('T')


@dataclass
class MergeContext():
    priority: Optional[int] = None
    order: Optional[int] = None
    terminal: Optional[bool] = False

    def get_priority(self) -> int:
        if self.priority is not None:
            return self.priority
        return 0

    def get_order(self) -> int:
        if self.order is not None:
            return self.order
        return 0

    def get_sort_key(self) -> Tuple[int, int]:
        return (-self.get_priority(), self.get_order())

    def allow_none(self):
        return False

    def is_terminal(self):
        return False

    def is_valid_key(self, key):
        return not key.startswith('$')

    def merge_in(self, other: 'MergeContext'):
        # TODO: convert to immutability
        if self.priority is None:
            self.priority = other.priority
        if self.order is None:
            self.order = other.order
        if self.terminal is None:
            self.terminal = other.terminal


@dataclass
class SparseTree(Generic[T]):
    """Tree structure that will return the most recent value in the traversal"""
    data: Optional[T] = None
    nodes: Dict[str, 'SparseTree[T]'] = field(default_factory=dict)

    def get_node(self, node: str) -> Optional['SparseTree[T]']:
        result = self.nodes.get(node)
        if result is not None:
            if result.data is None:
                return SparseTree(self.data, result.nodes)
            return result
        return None

    def get_node_default(self, node: str, data: T) -> 'SparseTree[T]':
        result = self.get_node(node)
        if result is not None:
            return result
        return SparseTree(data=data, nodes={})

    def get_or_persist(self, node: str) -> 'SparseTree[T]':
        return self.get_node_default(node, self.data)
