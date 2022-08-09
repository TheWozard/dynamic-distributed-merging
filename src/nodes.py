from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.context import MergeContext


def merge(documents: List['INode']) -> any:
    ordered = sorted([doc for doc in documents if doc is not None],
                     key=INode.get_sort_key)
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

    def node_from_id_index(self, _id: any, index: Optional[int]) -> Optional['INode']:
        context, is_important = self.context.context_from_id_index(_id, index)
        if is_important:
            return ValueNode(context, None)
        return None

    # Common merge function

    # Merges all passed objects together.
    # The passed list of docs is expected to already include self.
    # Passed documents are merged in order passed.
    @abstractmethod
    def merge_ordered(self, documents: List['INode']) -> any:
        pass

    @abstractmethod
    def willing_to_drive(self):
        pass

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
        # self.context.is_valid_key(key) is potentially a leaky abstraction of
        # how we are intending to load data. This should probably be removed.
        return [key for key in self.value if self.context.is_valid_key(key)]

    def node_from_key(self, key) -> Optional[INode]:
        if key in self.value:
            return data_to_node(self.context.context_from_key(key)[0], self.value[key])
        return super().node_from_key(key)

    def get_id(self) -> any:
        return self.context.get_id(self.value)

    def merge_ordered(self, documents: List[INode]) -> any:
        result = {}
        seen = set()
        for doc in documents:
            for key in doc.get_keys():
                if key not in seen:
                    seen.add(key)
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
        return self._node_cache

    def node_from_id_index(self, _id: any, index: Optional[int]) -> Optional[INode]:
        self._ensure_cache()
        if _id in self._id_cache:
            return self._id_cache[_id]
        return super().node_from_id_index(_id, index)

    def merge_ordered(self, documents: List[INode]) -> any:
        result = []
        ids_seen = set()
        for i, doc in enumerate(documents):
            for _id, node in doc.get_nodes():
                if _id is None or _id not in ids_seen:
                    ids_seen.add(_id)
                    other = documents[:]
                    other.pop(i)
                    value = merge([node] + [doc.node_from_id_index(_id, None) for doc in other])
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
            self._node_cache = []
            self._id_cache = {}
            for index, element in enumerate(self.value):
                _id = self.context.get_id(element)
                node = data_to_node(self.context.context_from_id_index(_id, index)[0], element)
                self._node_cache.append((_id, node))
                if _id is not None:
                    self._id_cache[_id] = node


def data_to_node(context: MergeContext, value: any) -> INode:
    """Converts an standard json value to its equivalent node"""
    if type(value) is dict:
        return DictNode(value=value, context=context)
    if type(value) is list:
        return ListNode(value=value, context=context)
    else:
        return ValueNode(value=value, context=context)
