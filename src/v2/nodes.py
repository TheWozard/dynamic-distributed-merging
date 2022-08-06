from abc import ABC
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.v2.context import MergeContext


def merge(documents: 'List[INode]') -> any:
    ordered = sorted([doc for doc in documents if doc is not None],
                     key=INode.get_sort_key)
    if len(ordered) == 0:
        return None
    for doc in ordered:
        if doc.willing_to_drive():
            return doc.merge_ordered(ordered)
    return None


@dataclass
class INode(ABC):
    """Interface for merge node as well as providing binding for context nodes"""
    context: MergeContext

    # Dict handling functions

    def get_keys(self) -> List[str]:
        return []

    def node_from_key(self, key: str) -> Optional['INode']:
        context, is_important = self.context.context_from_key(key)
        if is_important:
            return ValueNode(context, None)
        return None

    # List handling functions

    def get_nodes(self) -> List['INode']:
        return []

    def get_id(self, id_key='$key') -> any:
        return None

    def node_from_id(self, _id: any) -> Optional['INode']:
        context, is_important = self.context.context_from_id(_id)
        if is_important:
            return ValueNode(context, None)
        return None

    # Common merge function

    # Merges all passed objects together.
    # The passed list of docs is expected to already include self.
    # Passed documents are merged in order passed.
    def merge_ordered(self, documents: List['INode']) -> any:
        if len(documents) > 1 and not self.is_terminal():
            return documents[1].merge_ordered(documents[1:])
        return None

    def willing_to_drive(self):
        return False

    # Makes it easier to sort

    def get_sort_key(self):
        return self.context.get_sort_key()


@dataclass
class ValueNode(INode):
    value: any

    def merge_ordered(self, documents: List[INode]) -> any:
        # This is a special case. Because we already found the first element that is willing_to_drive
        # and that is the merge_ordered called we know we are the first value that ready to be merged and
        # thus do not need to iterate over documents.
        return self.value

    def willing_to_drive(self):
        return (self.value is not None or self.context.is_allow_none())


@dataclass
class DictNode(INode):
    value: Dict[str, any]

    def get_keys(self) -> List[str]:
        return [key for key in self.value if self.context.is_valid_key(key)]

    def node_from_key(self, key) -> Optional['INode']:
        if key in self.value:
            return data_to_node(self.context.context_from_key(key)[0], self.value[key])
        return super().node_from_key(key)

    def get_id(self, id_key='$id') -> any:
        if id_key in self.value:
            return self.value[id_key]
        return None

    def merge_ordered(self, documents: List[INode]) -> any:
        result = {}
        for i, doc in enumerate(documents):
            for key in doc.get_keys():
                if key not in result:
                    value = merge([doc.node_from_key(key) for doc in documents])
                    if value is not None or doc.context.is_allow_none():
                        result[key] = value
            if doc.context.is_terminal():
                break
        if len(result) > 0 or self.context.is_allow_empty():
            return result
        return None

    def willing_to_drive(self):
        return True


@dataclass
class ListNode(INode):
    value: List[any]
    _node_cache: Optional[List[INode]] = None
    _id_cache: Optional[Dict[str, INode]] = None

    def get_nodes(self):
        self._ensure_cache()
        return self._node_cache + super().get_nodes()

    def node_from_id(self, _id: any) -> Optional[INode]:
        self._ensure_cache()
        if _id in self._id_cache:
            return self._id_cache[_id]
        return super().node_from_id(_id)

    def merge_ordered(self, documents: List[INode]) -> any:
        result = []
        ids_seen = set()
        for i, doc in enumerate(documents):
            for node in doc.get_nodes():
                _id = node.get_id()
                if _id is None or _id not in ids_seen:
                    ids_seen.add(_id)
                    other = documents[:]
                    other.pop(i)
                    value = merge([node] + [doc.node_from_id(_id) for doc in other])
                    if value is not None or doc.context.is_allow_none():
                        result.append(value)
            if doc.context.is_terminal():
                break
        if len(result) > 0 or self.context.is_allow_empty():
            return result
        return None

    def willing_to_drive(self):
        return True

    def _ensure_cache(self):
        if self._node_cache is None or self._id_cache is None:
            self._node_cache = [data_to_node(None, element) for element in self.value]
            self._id_cache = {node.get_id(): node for node in self._node_cache if node.get_id() is not None}
            for node in self._node_cache:
                node.context = self.context.context_from_id(node.get_id())[0]


def data_to_node(context: MergeContext, value: any) -> 'INode':
    """Converts an standard json value to its equivalent node"""
    if type(value) is dict:
        return DictNode(value=value, context=context)
    if type(value) is list:
        return ListNode(value=value, context=context)
    else:
        return ValueNode(value=value, context=context)
