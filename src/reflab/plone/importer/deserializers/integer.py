def deserialize(value, **args):
    if value == 'None':
        return 0
    return int(value)
        