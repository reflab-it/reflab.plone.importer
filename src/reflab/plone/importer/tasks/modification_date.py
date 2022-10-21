# The modification_date attibute should be set after the creation of all the
# contents. The reason to do in this way is because in Plone when an item is
# added into a folder the folder modification is updated automatically

from plone.dexterity.utils import datify

def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")    
        return
    obj = container[obj_id]

    modification_date = data['fields'].get('modification_date', None)
    if not modification_date:
        importer.logger.warning(f"Missing 'modification_date' for {obj.absolute_url()}")
        return
    modification_date = datify(modification_date)    

    if modification_date != obj.modification_date:
        obj.setModificationDate(modification_date)
        obj.reindexObject(idxs=['modified'])
        importer.logger.info(f"Updated modification date of {obj.absolute_url()}")
    