from dataclasses import dataclass
from optparse import Option
from typing import Dict, Generator, Iterable, List, Optional, Tuple

from src.tree import MostRecentTree


@dataclass
class MergeContext:
    # The order the document is resolved in. Higher first.
    priority: int = 0
    # Used to resolve conflicts when priority is equal, should be unique across compared documents.
    # Generally this is the original order of the documents at the start of the merge.
    # Lower is first.
    order: int = 0
    # If, after the completion of this context, lower priority contexts should be evaluated.
    is_terminal: bool = False
    # In the absence of data, should this be considered in the merge.
    preserve_none: bool = False

    def get_sort_key(self):
        return (-self.priority, self.order)

    def is_valid_key(self, key: str):
        return not key.startswith("$")

    def get_element_key(self, element: any) -> Optional[str]:
        if type(element) is dict:
            return element.get("$id")
        else:
            return None


@dataclass
class ContextDocument:
    # Describes the current rules and state applied to this context
    context: MostRecentTree[MergeContext]

    def get_sort_key(self):
        return self.context.data.get_sort_key()

    def interested_keys(self) -> List[Tuple[str, any]]:
        return [(key, None) for key in self.context.nodes]

    def interested_elements(self) -> List[any]:
        return []

    def get_document(self, key: str) -> 'Optional[ContextDocument]':
        # if the context still has a branch that covers this key we continue to
        # participate as a ContextDocument
        if key in self.context.nodes:
            return ContextDocument(
                context=self.context.get_or_persist(key)
            )
        return None


@dataclass
class DictDocument(ContextDocument):
    data: Dict

    def interested_keys(self) -> List[Tuple[str, any]]:
        return super().interested_keys() + [
            (key, self.data.get(key)) for key in self.data if self.context.data.is_valid_key(key)
        ]

    def get_document(self, key: str):
        if key in self.data:
            if type(self.data[key]) is dict:
                return DictDocument(
                    data=self.data.get(key),
                    context=self.context.get_or_persist(key)
                )
            if type(self.data[key]) is list:
                return ListDocument(
                    data=self.data.get(key),
                    context=self.context.get_or_persist(key)
                )
        return super().get_document(key)


@dataclass
class ListDocument(ContextDocument):
    data: List

    def interested_keys(self):
        return []  # We dont want to expose list keys by accident through the context

    def interested_elements(self):
        return self.data

    def get_document(self, key: str):
        for element in self.data:
            if self.context.data.get_element_key(element) == key:
                return DictDocument(
                    data=element,
                    context=self.context.get_or_persist(key)
                )
        return super().get_document('n')
