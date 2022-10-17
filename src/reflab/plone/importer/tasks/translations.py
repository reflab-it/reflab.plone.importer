from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone import api

def task(importer, container, data):
    obj_id = data['id']
    obj = obj_id in container.objectIds() and container[obj_id] or None
    if not obj:
        return    

    translations = data.get('translations', {})
    if not translations:
        return

    if not ITranslatable.providedBy(obj):
        importer.logger.warning(f"Translations provided for {obj.absolute_url()} but can't be translated")

    tm = ITranslationManager(obj)
    current_translations = tm.get_translations().keys()

    for language, uid in translations.items():
        if language in current_translations:
            continue
        target = api.content.get(UID=uid)
        if not target:
             importer.logger.warning(f"Missing target object for {language} translation of {obj.absolute_url()}")
             continue
        tm.register_translation(language, target)

    importer.logger.info(f"All translations set on {obj.absolute_url()}")