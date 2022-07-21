from typing import Dict, List

from src.context import MergeContext, MergeDocument


def merge(*argv: Dict) -> Dict:
    return _merge_dict(*[
        MergeDocument(context=MergeContext(), document=document) for document in argv
    ])


def _merge_dict(*argv: MergeDocument) -> Dict:
    return argv[0].context.method()(*argv)


def _merge_list(*argv: List) -> List:
    # TODO
    pass
