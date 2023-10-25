def deserialize(value, **args):
    if value == 'None' or value is None:
        return 0
    return int(value)
        
