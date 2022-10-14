# This task expect that the references to set were temporary stored as a list
# of uid (usually during the standard craete task)

from plone import api
from plone.dexterity.utils import iterSchemata
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import Relation, RelationChoice, RelationList
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder


def task(importer, container, data):
    obj_id = data['id']
    obj = obj_id in container.objectIds() and container[obj_id] or None
    if not obj:
        return    

    intids = getUtility(IIntIds)

    for schemata in iterSchemata(obj):
        for name, field in getFieldsInOrder(schemata):   
             
            if type(field) in [Relation, RelationChoice, RelationList]:
                value = field.get(schemata(obj))
                if not value:
                    continue

                relations = []
                for uid in value:
                    target = api.content.get(UID=uid)
                    if target:
                        uuid = intids.getId(target)
                        relations.append(RelationValue(uuid))  

                if relations:
                    if type(field) == RelationList:
                        setattr(obj, name, relations)
                    else:
                        setattr(obj, name, relations[0])
                    importer.logger.info(f'Referecens to "{value}" set on {obj.absolute_url()}')

    importer.logger.info(
        f"Referecens set on {obj.absolute_url()}"
    )
