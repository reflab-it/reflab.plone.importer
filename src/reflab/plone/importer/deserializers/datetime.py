import datetime

def deserialize(value):
    if value is None or value == 'None':
        return None
    else:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
