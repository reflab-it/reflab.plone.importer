# The default page must be set as a separate task after the creation of all
# contents

def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        return
    
    obj = container[obj_id]    
    value = data.get('default_page', None)
    if not value:
        return    

    if obj.hasProperty('default_page'):
        obj._updateProperty('default_page', value)
    else:
        obj._setProperty('default_page', value, 'string')  

    importer.logger.info(f'Default page "{value}" set on {obj.absolute_url()}')

