from typing import Callable, Dict, List
from dataclasses import dataclass


class MergeContext:

    def priority(self) -> int:
        return 0

    def method(self) -> Callable[..., Dict]:
        return outer_merge


@dataclass
class MergeDocument:
    context: MergeContext
    document: List | Dict


def outer_merge(*argv: MergeDocument) -> Dict:
    seen = set()
    output = {}
    for doc in argv:
        unique = set(doc.document.keys()).difference(seen)
        for key in unique:
            output[key] = doc.document[key]
        seen = seen.union(unique)
    return output
