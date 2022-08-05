from abc import ABC
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.v2.context import MergeContext


def merge(documents: 'List[INode]') -> any:
    ordered = sorted([doc for doc in documents if doc is not None],
                     key=INode.get_sort_key)
    if len(ordered) == 0:
        return None
    # The highest priority non None document determines how the data gets merged.
    return ordered[0].merge_ordered(ordered)


@dataclass
class INode(ABC):
    context: MergeContext

    # Value handling functions

    # Returns a tuple of both the value and if the value should be used
    # This is because None can be a valid value in some cases
    def get_value(self) -> Tuple[any, bool]:
        return None, False

    # Dict handling functions

    def get_keys(self) -> List[str]:
        return []

    def node_from_key(self) -> Optional['INode']:
        return None

    # List handling functions

    def get_nodes(self) -> List['INode']:
        return []

    def get_id(self, id_key='$key') -> any:
        return None

    def node_from_id(self, _id: any) -> Optional['INode']:
        return None

    # Common merge function

    # Merges all passed objects together.
    # The passed list of docs is expected to already include self.
    # Passed documents are merged in order passed.
    def merge_ordered(self, documents: List['INode']) -> any:
        if len(documents) > 1 and not self.is_terminal():
            return documents[1].merge_ordered(documents[1:])
        return None

    # Makes it easier to sort

    def get_sort_key(self):
        return self.context.get_sort_key()


@dataclass
class ValueNode(INode):
    value: any

    def get_value(self) -> Tuple[any, bool]:
        return self.value, (self.value != None or self.context.allow_none())

    def merge_ordered(self, documents: List[INode]) -> any:
        for doc in documents:
            value, ok = doc.get_value()
            if ok:
                return value
            if doc.context.is_terminal():
                break
        return None


@dataclass
class DictNode(INode):
    value: Dict[str, any]

    def get_keys(self) -> List[str]:
        return [key for key in self.value if self.context.is_valid_key(key)]

    def node_from_key(self, key) -> Optional['INode']:
        if key in self.value:
            return data_to_node(self.value[key])
        return None

    def get_id(self, id_key='$id') -> any:
        if id_key in self.value:
            return self.value[id_key]
        return None

    def merge_ordered(self, documents: List[INode]) -> any:
        result = {}
        for i, doc in enumerate(documents):
            for key in doc.get_keys():
                if key not in result:
                    result[key] = merge([doc.node_from_key(key)
                                        for doc in documents[i:]])
            if doc.context.is_terminal():
                break
        return result


@dataclass
class ListNode(INode):
    value: List[any]
    _node_cache: Optional[List[INode]] = None
    _id_cache: Optional[Dict[str, INode]] = None

    def get_nodes(self):
        self._ensure_node_cache()
        return self._node_cache + super().get_nodes()

    def node_from_id(self, _id: any) -> Optional[INode]:
        self._ensure_id_cache()
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
                    result.append(
                        merge([node] + [doc.node_from_id(_id) for doc in documents[i+1:]]))
            if doc.context.is_terminal():
                break
        return result

    def _ensure_node_cache(self):
        if self._node_cache is None:
            self._node_cache = [
                data_to_node(element) for element in self.value
            ]

    def _ensure_id_cache(self):
        if self._id_cache is None:
            self._ensure_node_cache()
            self._id_cache = {
                node.get_id(): node for node in self._node_cache if node.get_id() is not None
            }

# Converts an standard json value to its equivalent node


def data_to_node(value: any, context=MergeContext()) -> 'INode':
    if type(value) is dict:
        return DictNode(
            value=value,
            context=context,
        )
    if type(value) is list:
        return ListNode(
            value=value,
            context=context,
        )
    else:
        return ValueNode(
            value=value,
            context=context,
        )
