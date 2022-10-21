def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")    
        return
        
    obj = container[obj_id]
    obj.reindexObject(idxs=['allowedRolesAndUsers'])
    importer.logger.info(f"Reidexed security of {obj.absolute_url()}")    
