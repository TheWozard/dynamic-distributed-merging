from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class MergeData():
    priority: Optional[int] = None
    order: Optional[int] = None

    terminal: Optional[bool] = None
    allow_none: Optional[bool] = None
    allow_empty: Optional[bool] = None

    def get_priority(self):
        return self.priority or 0

    def get_order(self):
        return self.order or 0

    def get_sort_key(self):
        return (-self.get_priority(), self.get_order())

    def is_allow_none(self):
        return self.allow_none or False

    def is_allow_empty(self):
        return self.allow_empty or False

    def is_terminal(self):
        return self.terminal or False

    def is_valid_key(self, key):
        return not key.startswith('$')

    # Node behavior

    def update(self, other: 'MergeData'):
        self.priority = self.priority if self.priority is not None else other.priority
        self.order = self.order if self.order is not None else other.order
        self.terminal = self.terminal if self.terminal is not None else other.terminal
        self.allow_none = self.allow_none if self.allow_none is not None else other.allow_none
        self.allow_empty = self.allow_empty if self.allow_empty is not None else other.allow_empty

        return self


@dataclass
class MergeContext(MergeData):

    def context_from_key(self, key: str) -> Tuple['MergeContext', bool]:
        return self, False

    def context_from_id(self, _id: any) -> Tuple['MergeContext', bool]:
        return self, False


@dataclass
class DictMergeContext(MergeContext):
    nodes: Dict[str, MergeContext] = field(default_factory=dict)

    def is_important(self):
        return True

    def context_from_key(self, key: str) -> Tuple['MergeContext', bool]:
        if key in self.nodes:
            return self.nodes[key].update(self), True
        return MergeContext().update(self), False


@dataclass
class ListMergeContext(MergeContext):
    ids: Dict[any, MergeContext] = field(default_factory=dict)
    default: Optional[MergeContext] = None

    def context_from_id(self, _id: any) -> Tuple['MergeContext', bool]:
        if _id is None:
            return self.default.update(self), True
        if _id in self.nodes:
            return self.nodes[_id].update(self), True
        return MergeContext().update(self), False
