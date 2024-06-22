import json


def string_to_dict(value):
    """str to dict, replace '' with None"""
    if not value:
        return None
    values = json.loads(value)
    for key in values:
        if values[key] == "":
            values[key] = None

    return values
