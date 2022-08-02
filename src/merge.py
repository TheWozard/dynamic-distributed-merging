from typing import Dict, List

from src.context import ValueDocument, DictDocument, ListDocument, MergeContext
from src.tree import MostRecentTree


def no_context_merge(*argv: Dict) -> Dict:
    return _merge_dicts(*[
        DictDocument(context=MostRecentTree(MergeContext(order=index)), data=document) for index, document in enumerate(argv)
    ])


def _merge_dicts(*argv: ValueDocument) -> Dict:
    final = {}
    docs = sorted([doc for doc in argv if doc is not None],
                  key=ValueDocument.get_sort_key)
    for index, doc in enumerate(docs):
        unprocessed_docs = docs[index:]
        for key, value in doc.interested_keys():
            if key not in final:

                # Act
                if type(value) is dict:
                    final[key] = _merge_dicts(*[
                        doc.get_document_by_key(key) for doc in unprocessed_docs
                    ])
                elif type(value) is list:
                    final[key] = _merge_lists(*[
                        doc.get_document_by_key(key) for doc in unprocessed_docs
                    ])
                elif value is not None or doc.context.data.preserve_none:
                    final[key] = value
                else:
                    for doc in unprocessed_docs[1:]:
                        key_doc = doc.get_document_by_key(key)
                        value = key_doc.get_value()
                        if value is not None or key_doc.context.data.preserve_none:
                            final[key] = value
                            break

        if doc.context.data.is_terminal:
            return final
    return final


def _merge_lists(*argv: ValueDocument) -> List:
    final = []
    seen_ids = set()
    docs = sorted([doc for doc in argv if doc is not None],
                  key=ValueDocument.get_sort_key)
    for index, doc in enumerate(docs):
        other_docs = docs[index + 1:]
        for ele_index, element in doc.interested_elements():

            # Act
            if type(element) is dict:
                id_ = doc.context.data.get_element_id(element)
                if id_ is None:
                    final.append(_merge_dicts(*([doc.get_document_by_index(ele_index)] + [
                        doc.get_document_by_id(id_) for doc in other_docs
                    ])))
                elif id_ not in seen_ids:
                    seen_ids.add(id_)
                    final.append(_merge_dicts(*([doc.get_document_by_index(ele_index)] + [
                        doc.get_document_by_id(id_) for doc in other_docs
                    ])))
            elif type(element) is list:
                final.append(_merge_lists(*([doc.get_document_by_index(ele_index)] + [
                    doc.get_document_by_id(None) for doc in other_docs
                ])))
            elif element is not None:
                final.append(element)
            elif doc.context.data.preserve_none:
                final.append(element)

        if doc.context.data.is_terminal:
            return final
    return final
