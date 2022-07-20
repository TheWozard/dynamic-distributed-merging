from typing import Dict, List


def merge(*argv: List[Dict]) -> Dict:
    return _merge_dict(*argv)


def _merge_dict(*argv: List[Dict]) -> Dict:
    # TODO
    return argv[0]


def _merge_list(*argv: List[List]) -> List:
    # TODO
    pass
