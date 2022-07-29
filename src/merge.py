from typing import Dict, List

from src.context import ContextDocument, DictDocument, ListDocument, MergeContext
from src.tree import MostRecentTree


def no_context_merge(*argv: Dict) -> Dict:
    return _merge_dicts(*[
        DictDocument(context=MostRecentTree(MergeContext(order=index)), data=document) for index, document in enumerate(argv)
    ])


def _merge_dicts(*argv: ContextDocument) -> Dict:
    final = {}
    docs = sorted(argv, key=ContextDocument.get_sort_key)
    for index, doc in enumerate(docs):
        for key, value in doc.interested_keys():
            if key not in final:

                # Act
                if type(value) is dict:
                    final[key] = _merge_dicts(*list(filter(None, [
                        doc.get_document(key) for doc in docs[index:]
                    ])))
                elif type(value) is list:
                    final[key] = _merge_lists(*list(filter(None, [
                        doc.get_document(key) for doc in docs[index:]
                    ])))
                elif value is not None:
                    final[key] = value
                elif doc.context.data.preserve_none:
                    final[key] = value

        if doc.context.data.is_terminal:
            return final
    return final


def _merge_lists(*argv: ContextDocument) -> List:
    final = []
    seen_keys = set()
    docs = sorted(argv, key=ContextDocument.get_sort_key)
    for index, doc in enumerate(docs):
        for element in doc.interested_elements():

            # Act
            if type(element) is dict:
                participants = []
                key = doc.context.data.get_element_key(element)
                if key is None:
                    final.append(_merge_dicts(*list(filter(None, [
                        DictDocument(
                            context=doc.context.get_or_persist('n'),
                            data=element
                        )
                    ] + [
                        doc.get_document('n') for doc in docs[index+1:]
                    ]))))
                elif key not in seen_keys:
                    seen_keys.add(key)
                    for doc in docs[index:]:
                        focused = doc.get_document(key)
                        if focused is not None:
                            participants.append(focused)
                        else:
                            participants.append(doc.get_document('n'))
                    final.append(_merge_dicts(
                        *list(filter(None, participants))))
            elif type(element) is list:
                final.append(_merge_lists(*list(filter(None, [
                    ListDocument(
                        context=doc.context.get_or_persist('n'),
                        data=element
                    )
                ] + [
                    doc.get_document('n') for doc in docs[index+1:]
                ]))))
            elif element is not None:
                final.append(element)
            elif doc.context.data.preserve_none:
                final.append(element)

        if doc.context.data.is_terminal:
            return final
    return final
