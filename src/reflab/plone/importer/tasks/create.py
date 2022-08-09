from  plone import api

CREATE_GLOBALS = dict(
    limit = 0, # edit here for debug purposes
    counter = 0
)

def task(importer, container, data):
    
    if CREATE_GLOBALS['limit'] > 0:
        if CREATE_GLOBALS['counter'] > CREATE_GLOBALS['limit']:
            return 

    id = data['id']
    if id in container.objectIds():
        importer.logger.warning(
            f"Already exists {id} in {'/'.join(container.getPhysicalPath())}"
        )
        return

    attributes = importer.deserialize_fields(data['fields'])
    
    for invalid_name in ['id', 'type', 'container']:
        if invalid_name in attributes.keys():
            importer.logger.warning(
                f"A field with name '{invalid_name}' can't be used during the\
                creation of a '{data['portal_type']}' and it will be ignored."
            )
            del(attributes[invalid_name])

    api.content.create(
        container = container,
        type = data['portal_type'],
        id = data['id'],
        **attributes
    )

    CREATE_GLOBALS['counter'] += 1

    importer.logger.info(
        f"Created {id} in {'/'.join(container.getPhysicalPath())}"
    )