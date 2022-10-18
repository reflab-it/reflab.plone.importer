from  plone import api
from plone.uuid.interfaces import ATTRIBUTE_NAME as UID_ATTRIBUTE_NAME
from Products.CMFCore.interfaces import IFolderish


def task(importer, container, data):
    id = data['id']
    
    if not IFolderish.providedBy(container):
        importer.logger.error(f"Item in {container.absolute_url()} is not a container; '{id} not created'")
        return

    if id in container.objectIds():
        importer.logger.warning(
            f"Already exists {id} in {'/'.join(container.getPhysicalPath())}"
        )
        return

    attributes = data['fields']
    for invalid_name in ['id', 'type', 'container']:
        if invalid_name in attributes.keys():
            importer.logger.debug(
                f"A field with name '{invalid_name}' can't be used during the\
                creation of a '{data['portal_type']}' and it will be ignored."
            )
            del(attributes[invalid_name])

    portal_type = data['portal_type']
    available_types = api.portal.get_tool('portal_types').objectIds()
    if portal_type not in available_types:
        importer.logger.warning(f'The portal type {portal_type} is not availabe, it will be ignored')
        return
    
    obj = api.content.create(
        container = container,
        type = data['portal_type'],
        id = data['id'],
        **attributes
    )

    # if available, set also the UID
    uid = data.get('UID')
    if uid:
        setattr(obj, UID_ATTRIBUTE_NAME, data['UID'])
        obj.reindexObject(idxs=['UID'])

    # if available, set also the properties
    for property_name, property_value in data.get('properties', {}).items():
        if obj.hasProperty(property_name):
            obj._updateProperty(property_name, property_value)
        else:
            property_value_type = type(property_value)
            if property_value_type == str:
                obj._setProperty(property_name, property_value, 'string')        
            elif property_value_type == list:
                obj._setProperty(property_name, property_value, 'list')
            elif property_value_type == bool:
                obj._setProperty(property_name, property_value, 'boolean')                
            else:
                importer.logger.warning(f'Unsupported property type {property_value_type}')

    importer.logger.info(
        f"Created {id} in {'/'.join(container.getPhysicalPath())}"
    )