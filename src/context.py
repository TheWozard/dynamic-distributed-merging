from typing import Callable, Dict, List
from dataclasses import dataclass


@dataclass
class MergeContext:
    # The order the document is resolved in. Higher first.
    priority: int = 0
    # Used to resolve conflicts when priority is equal, should be unique across compared documents.
    # Generally this is the original order of the documents at the start of the merge.
    # Lower is first.
    order: int = 0
    # If none values should be considered a valid value.
    allow_nones: bool = True
    # If, after the completion of this context, lower priority contexts should be evaluated.
    terminal: bool = False


@dataclass
class MergeDocument:
    context: MergeContext
    document: List | Dict

    def valid_keys(self):
        for key in self.document:
            if not key.startswith("$") and (self.context.allow_nones or self.document[key] != None):
                yield key, self.document[key]

    def get_sort_key(self):
        return (-self.context.priority, self.context.order)


def outer_merge(*argv: MergeDocument) -> Dict:
    seen = set()
    output = {}
    for doc in argv:
        unique = set(doc.document.keys()).difference(seen)
        for key in unique:
            output[key] = doc.document[key]
        seen = seen.union(unique)
    return output
