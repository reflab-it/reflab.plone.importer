def deserialize(value, **args):
    if value is None:
        return ()
    return tuple(value)