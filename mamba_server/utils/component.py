""" Mamba generic utility functions for components """


def merge_dicts(dict_1, dict_2):
    """
    Merge dictionary dict_2 into dict_1. In case of conflict dict_1
    has precedence
    """
    if dict_1 is None:
        return dict_2

    if dict_2 is None:
        return dict_1

    result = dict_1
    for key in dict_2:
        if key in dict_1:
            if isinstance(dict_1[key], dict) and isinstance(dict_2[key], dict):
                merge_dicts(dict_1[key], dict_2[key])
        else:
            result[key] = dict_2[key]
    return result
