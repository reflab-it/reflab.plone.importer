from plone import api

def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        return

    review_state = data.get('review_state', None)
    if not review_state:
        return

    obj = container[obj_id]
    api.content.transition(obj=obj, to_state=review_state)    
    importer.logger.info(f"Updated review state of { '/'.join(obj.getPhysicalPath()) }")
