import os
from plone.namedfile import NamedBlobImage

def deserialize(value, **kwargs):
    fs_path = kwargs.get('fs_path')
    file_dir_path = os.path.join(fs_path, value)
    dir_contents = os.listdir(file_dir_path)
    if len(dir_contents) != 1:
        raise ValueError(f'Expected only one file in directory: {file_dir_path}')
    file_name = dir_contents[0]
    file_path = os.path.join(file_dir_path, file_name)

    with open(file_path, 'rb') as f:
        file_data = f.read()

    result = NamedBlobImage(data=file_data, filename=file_name)
    return result
