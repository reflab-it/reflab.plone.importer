import os
from plone.namedfile import NamedBlobFile

# TODO: define a best practice for exporting the value, options could be:
# - keep the value empty, use a convention to search file in a directory with
#   name '_{field_name}'
# - put a relative path of the directory that contains the file(s)

def deserialize(value, **kwargs):
    if value:
        fs_path = kwargs.get('fs_path')
        file_dir_path = os.path.join(fs_path, value)
        dir_contents = os.listdir(file_dir_path)
        if len(dir_contents) != 1:
            raise ValueError(f'Expected only one file in directory: {fs_path}')
        file_name = dir_contents[0]
        file_path = os.path.join(file_dir_path, file_name)

        with open(file_path, 'rb') as f:
            file_data = f.read()

        result = NamedBlobFile(data=file_data, filename=file_name)
    else:
        # no file exported
        result = None

    return result
