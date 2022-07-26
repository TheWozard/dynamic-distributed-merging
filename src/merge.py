from typing import Dict, List

from src.context import MergeContext, MergeDocument


def merge(*argv: Dict) -> Dict:
    return _merge_dict(*[
        MergeDocument(context=MergeContext(order=index), document=document) for index, document in enumerate(argv)
    ])


def _merge_dict(*argv: MergeDocument) -> Dict:
    final = {}
    seen = set()
    docs = sorted(argv, key=MergeDocument.get_sort_key)
    for index, doc in enumerate(docs):
        for key, value in doc.valid_keys():
            if key not in seen:
                seen.add(key)
                if type(value) is dict:
                    final[key] = _merge_dict(
                        *_get_all_of_key(key, docs[index:]))
                elif type(value) is list:
                    final[key] = _merge_list(
                        *_get_all_of_key(key, docs[index:]))
                else:
                    final[key] = value
        if doc.context.terminal:
            return final
    return final


def _merge_list(*argv: List) -> List:
    # TODO
    pass


def _get_all_of_key(key: str, docs: List[MergeDocument]) -> List:
    return [MergeDocument(context=doc.context, document=doc.document.get(key, None)) for doc in docs]
