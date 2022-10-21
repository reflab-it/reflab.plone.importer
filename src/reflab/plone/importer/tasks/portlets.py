
from zope.component import queryUtility
from plone.portlets.interfaces import IPortletManager
from zope.component import queryMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.component.interfaces import IFactory
from plone.portlets.interfaces import IPortletAssignmentSettings
from zope.component import getUtility
from plone.app.portlets.interfaces import IPortletTypeInterface
from zope.globalrequest import getRequest
from plone.restapi.interfaces import IFieldDeserializer
from plone.portlets.interfaces import ILocalPortletAssignmentManager

def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        return

    obj = container[obj_id]
    
    portlets_local = data.get('portlets', {}).get('local', {})
    portlets_blacklist = data.get('portlets', {}).get('blacklist', [])
    request = getRequest()

    for manager_name, portlets in portlets_local.items():
        manager = queryUtility(IPortletManager, manager_name)
        if not manager:
            importer.logger.info(u"No portlet manager {}".format(manager_name))
            continue
        mapping = queryMultiAdapter((obj, manager), IPortletAssignmentMapping)

        for portlet_data in portlets:
            # 1. Create the assignment
            assignment_data = portlet_data["assignment"]
            portlet_type = portlet_data["type"]
            portlet_factory = queryUtility(IFactory, name=portlet_type)
            if not portlet_factory:
                importer.logger.info(u"No factory for portlet {}".format(portlet_type))
                continue

            assignment = portlet_factory()
            
            name = portlet_data.get("name")
            if name in mapping:
                importer.logger.warning(f"Portlet {name} alredy exists in {obj.absolute_url()} and will be replaced")
                del mapping[name]
            mapping[name] = assignment

            # aq-wrap it so that complex fields will work
            assignment = assignment.__of__(importer.portal)

            # set visibility setting
            visible = portlet_data.get("visible")
            if visible:
                settings = IPortletAssignmentSettings(assignment)
                settings["visible"] = visible

            # 2. Apply portlet settings
            portlet_interface = getUtility(IPortletTypeInterface, name=portlet_type)
            for property_name, value in assignment_data.items():
                field = portlet_interface.get(property_name, None)
                if field is None:
                    continue
                field = field.bind(assignment)
                # deserialize data (e.g. for RichText)
                deserializer = queryMultiAdapter((field, obj, request), IFieldDeserializer)
                if deserializer is not None:
                    try:
                        value = deserializer(value)
                    except Exception as e:
                        importer.logger.warning(f"Failed to deserialize '{property_name}' of portlet {name} in {obj.absolute_url()}. Provided value is used")  
                field.set(assignment, value)

            importer.logger.info(u"Added {} '{}' to {} of {}".format(
                portlet_type, name, manager_name, obj.absolute_url()))

    for blacklist_status in portlets_blacklist:
        status = blacklist_status["status"]
        manager_name = blacklist_status["manager"]
        category = blacklist_status["category"]
        manager = queryUtility(IPortletManager, manager_name)
        if not manager:
            importer.logger.info("No portlet manager {}".format(manager_name))
            continue
        assignable = queryMultiAdapter((obj, manager), ILocalPortletAssignmentManager)
        if status.lower() == "block":
            assignable.setBlacklistStatus(category, True)
        elif status.lower() == "show":
            assignable.setBlacklistStatus(category, False)

    importer.logger.info(
        f"Portles set on {obj.absolute_url()}"
    )

    