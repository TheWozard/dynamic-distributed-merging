from dataclasses import dataclass, field
from typing import Dict, Generic, Optional, TypeVar

T = TypeVar('T')


@dataclass
class MostRecentTree(Generic[T]):
    """Tree structure that will return the most recent value in the traversal"""
    data: Optional[T] = None
    nodes: Dict[str, 'MostRecentTree[T]'] = field(default_factory=dict)

    def get_node(self, node: str) -> Optional['MostRecentTree[T]']:
        result = self.nodes.get(node)
        if result is not None:
            if result.data is None:
                return MostRecentTree(self.data, result.nodes)
            return result
        return None

    def get_node_default(self, node: str, data: T) -> 'MostRecentTree[T]':
        result = self.get_node(node)
        if result is not None:
            return result
        return MostRecentTree(data=data, nodes={})

    def get_or_persist(self, node: str) -> 'MostRecentTree[T]':
        return self.get_node_default(node, self.data)
