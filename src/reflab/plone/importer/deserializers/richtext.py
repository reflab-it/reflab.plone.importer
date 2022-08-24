from plone.app.textfield.value import RichTextValue

def deserialize(value, **args):
    return RichTextValue(
        raw=value,
        mimeType='text/plain',
        outputMimeType='text/x-html-safe'
    )