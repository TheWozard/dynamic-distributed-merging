from dataclasses import dataclass
from optparse import Option
from typing import ClassVar, Dict, Generator, Iterable, List, Optional, Tuple

from src.tree import MostRecentTree


@dataclass
class MergeContext:
    # Key that if present provides the id of an element in a list.
    element_id_key: ClassVar[str] = "$id"
    # Prefix that causes an key to be skipped in a dict.
    ignore_prefix: ClassVar[str] = "$"
    # Key used to match the any case for a list
    list_any_key: ClassVar[str] = "*"

    # The order the document is resolved in. Higher first.
    priority: int = 0
    # Used to resolve conflicts when priority is equal, should be unique across compared documents.
    # Generally this is the original order of the documents at the start of the merge.
    # Lower is first.
    order: int = 0
    # If, after the completion of this context, lower priority contexts should be evaluated.
    is_terminal: bool = False
    # Does this context consider None to be a valid value.
    preserve_none: bool = False

    def get_sort_key(self):
        """Used to sort the order of contexts."""
        return (-self.priority, self.order)

    def is_valid_key(self, key: str):
        """Identifies if a key provided in the data should be considered."""
        return not key.startswith(MergeContext.ignore_prefix)

    def get_element_id(self, element: any) -> Optional[str]:
        """Converts an element to an id. Used to match elements in a list."""
        if type(element) is dict:
            return element.get(MergeContext.element_id_key)
        else:
            return None


@dataclass
class ValueDocument:
    context: MostRecentTree[MergeContext]
    data: any = None

    def get_sort_key(self):
        return self.context.data.get_sort_key()

    def get_value(self) -> any:
        return self.data

    def interested_keys(self) -> List[Tuple[str, any]]:
        return [(key, None) for key in self.context.nodes]

    def interested_elements(self) -> List[Tuple[int, any]]:
        return []

    def get_document_by_key(self, key: str) -> 'Optional[ValueDocument]':
        # if the context still has a branch that covers this key we continue to
        # participate as a ContextDocument
        if key in self.context.nodes:
            return ValueDocument(
                context=self.context.get_or_persist(key)
            )
        return None

    def get_document_by_id(self, id_: Optional[str]):
        return None

    def get_document_by_index(self, index: int):
        return None


@dataclass
class DictDocument(ValueDocument):
    data: Dict[str, any]

    def get_value(self) -> any:
        return None

    def interested_keys(self) -> List[Tuple[str, any]]:
        return super().interested_keys() + [
            (key, self.data.get(key)) for key in self.data if self.context.data.is_valid_key(key)
        ]

    def get_document_by_key(self, key: str):
        if key in self.data:
            return create_document_from_value(
                data=self.data[key],
                context=self.context.get_or_persist(key)
            )
        return super().get_document_by_key(key)


class ListDocument(ValueDocument):

    def __init__(self, data: List, context: MostRecentTree[MergeContext]):
        super().__init__(context=context)
        self.data: List[any] = data
        self.lookup: Dict[str, any] = {}
        for element in data:
            id_ = self.context.data.get_element_id(element)
            if id_ is not None:
                self.lookup[id_] = element

    def get_value(self) -> any:
        return None

    def interested_keys(self):
        return []  # We dont want to expose list keys by accident through the context

    def interested_elements(self):
        return enumerate(self.data)

    def get_document_by_key(self, key: str):
        return None

    def get_document_by_id(self, id_: str):
        if id_ in self.lookup:
            context = self.context.get_node(id_)
            if context is None:
                context = self.context.get_or_persist(
                    MergeContext.list_any_key)
            return create_document_from_value(
                data=self.lookup[id_],
                # This is really awkward as we are mixing id and key
                context=context
            )
        return create_document_from_value(
            data=None,
            context=self.context.get_or_persist(MergeContext.list_any_key)
        )

    def get_document_by_index(self, index: int):
        if index <= len(self.data):
            return create_document_from_value(
                data=self.data[index],
                context=self.context.get_or_persist(MergeContext.list_any_key)
            )
        return create_document_from_value(
            data=None,
            context=self.context.get_or_persist(MergeContext.list_any_key)
        )


def create_document_from_value(context: MostRecentTree[MergeContext], data=None):
    if type(data) is dict:
        return DictDocument(
            data=data,
            context=context,
        )
    if type(data) is list:
        return ListDocument(
            data=data,
            context=context,
        )
    else:
        return ValueDocument(
            data=data,
            context=context,
        )
