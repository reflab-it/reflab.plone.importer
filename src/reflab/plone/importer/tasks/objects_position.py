def task(importer, container, data):
    ordered_ids = data.get('positions', [])
    if not ordered_ids:
        return

    obj_id = data['id']
    obj = obj_id in container.objectIds() and container[obj_id] or None
    if not obj:
        return

    obj = container[obj_id]
    errors = []
    for position, id in enumerate(ordered_ids):
        try:
            if obj.moveObjectToPosition(id, position, suppress_events=True):
                obj[id].reindexObject(idxs=['getObjPositionInParent'])
        except ValueError as err:
            errors.append(id)
        except Exception as err:
            importer.logger.error(f'Unexpected error while moving "{id}" of {obj.absolute_url()}')

    if errors:
        importer.logger.warning(f'Failed to move "{errors}" of {obj.absolute_url()}')
    else:
        importer.logger.info(f'Ordered all objects of {obj.absolute_url()}')
