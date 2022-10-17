from plone.app.textfield.value import RichTextValue
from plone.app.multilingual.interfaces import ITranslationManager

def deserialize(value, **args):
    return RichTextValue(
        raw=value,
        mimeType='text/html',
        outputMimeType='text/x-html-safe'
    )