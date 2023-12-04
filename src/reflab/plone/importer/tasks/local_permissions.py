
def task(importer, container, data):
    """ fix ownership and local_roles """
    obj_id = data['id']
    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")
        return

    obj = container[obj_id]
    importer.logger.info(f"Processing {obj_id} in {container.absolute_url()}")

    #creators = data['fields'].get('creators')
    #if creators:
    #    obj.setCreators(creators)

    obj._owner = data['ownership']
    obj.__ac_local_roles__ = data['local_roles']
    obj.__ac_local_roles_block__ = data['block_inherit']

    importer.logger.info(f"Updated {obj_id} in {container.absolute_url()}: owner: {obj._owner} - roles: {obj.__ac_local_roles__}")
