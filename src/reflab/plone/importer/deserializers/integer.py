def deserialize(value, **args):
    if value == 'None' or value is None:
        return None
    return int(value)
