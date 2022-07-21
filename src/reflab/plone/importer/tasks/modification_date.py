# The modification_date attibute should be set after the creation of all the
# contents. The reason to do in this way is because in Plone when an item is
# added into a folder the folder modification is updated automatically

def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        return

    modification_date = data['fields'].get('modification_date', None)
    if not modification_date:
        return

    obj = container[obj_id]
    setattr(obj, 'modification_date', modification_date['value'])
    obj.reindexObject(idxs=['modification_date'])
    importer.logger.info(f"Updated modification date of { '/'.join(obj.getPhysicalPath()) }")
    