from DateTime import DateTime
from plone.event.utils import pydt

def deserialize(value, **args):
    if not value or value == 'None' :
        return None
    else:
        return pydt(DateTime(value))
