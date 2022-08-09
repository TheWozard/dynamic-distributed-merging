from dataclasses import dataclass
from typing import Dict, List, Optional
from src.context import DictMergeContext, ListMergeContext, MergeContext
from src.nodes import INode, data_to_node


@dataclass
class _extractor():
    priority_key = '$priority'
    terminal_key = '$terminal'
    allow_none_key = '$allow_none'
    allow_empty_key = '$allow_empty'

    def get_dict_context(self, raw: Dict, nodes: Optional[Dict[str, MergeContext]]) -> MergeContext:
        if ((nodes is not None and len(nodes) > 0) or self.priority_key in raw or self.terminal_key in raw
                or self.allow_none_key in raw or self.allow_empty_key in raw):
            return DictMergeContext(
                priority=raw.get(self.priority_key),
                terminal=raw.get(self.terminal_key),
                allow_none=raw.get(self.allow_none_key),
                allow_empty=raw.get(self.allow_empty_key),
                nodes=nodes,
            )
        return None

    def get_list_context(self, raw: List, index: Optional[List[MergeContext]]) -> MergeContext:
        return DictMergeContext(index=index)


def _extract_embedded_context(raw: any, extractor: _extractor) -> MergeContext:
    if type(raw) is dict:
        nodes = {}
        for key in raw:
            temp = _extract_embedded_context(raw[key], extractor)
            if temp is not None:
                nodes[key] = temp
        return extractor.get_dict_context(raw, nodes)
    if type(raw) is list:
        return ListMergeContext(
            index=[_extract_embedded_context(item, extractor) for item in raw]
        )
    else:
        return None


def _extract(raw: any, extractor=_extractor()) -> MergeContext:
    embedded = _extract_embedded_context(raw, extractor)
    if embedded is not None:
        return embedded
    return MergeContext()


def parse_context(raw: any) -> INode:
    return data_to_node(context=_extract(raw), value=raw)
