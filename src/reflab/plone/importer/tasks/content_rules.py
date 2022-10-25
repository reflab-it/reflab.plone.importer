from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager


def task(importer, container, data):
    """ """
    obj_id = data['id']
    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")
        return

    obj = container[obj_id]

    content_rules = data.get('content-rules', None)
    if not content_rules:
        importer.logger.warning(f"Missing 'content rules' for {obj.absolute_url()}")
        return

    manager = IRuleAssignmentManager(obj)

    # clean
    for name in manager.keys():
        del manager[name]

    # restore config
    for name, rule in content_rules.items():
        manager[name] = RuleAssignment(name,
                                       enabled=rule['enabled'],
                                       bubbles=rule['bubbles'])

    #print(obj,id, current_content_rules(obj, {}))
    importer.logger.info(f"Updated 'content rules' of {obj.absolute_url()}")


def current_content_rules(obj, data):
    # for debug purpouse
    manager = IRuleAssignmentManager(obj)

    rules = {}
    for name, rule in manager.items():
        rules[name] = dict(enabled=rule.enabled, bubbles=rule.enabled)

    data['content-rules'] = rules
    return data