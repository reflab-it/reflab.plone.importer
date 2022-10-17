from decimal import Decimal

def deserialize(value, **args):
    if value is None:
        return None
    return Decimal(value)