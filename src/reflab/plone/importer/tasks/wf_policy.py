from plone.event.utils import pydt
from DateTime import DateTime
from persistent.mapping import PersistentMapping
from plone import api


def task(importer, container, data):
    """ """
    obj_id = data['id']

    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")    
        return
    obj = container[obj_id]

    if '.wf_policy_config' in data:
        importer.logger.info(f"Updating 'wp_policy_config' of {obj.absolute_url()}")
    else:
        importer.logger.info(f"No 'wp_policy_config' for {obj.absolute_url()}")
        return

    workflow_policy_in = data['.wf_policy_config']['workflow_policy_in']
    workflow_policy_below = data['.wf_policy_config']['workflow_policy_below']

    if not '.wf_policy_config' in obj.objectIds():
        importer.logger.info(f"Created local 'wf_policy_config' of {obj.absolute_url()}")
        # create new workflow policy config
        wfp = WorkflowPolicyConfig(workflow_policy_in, workflow_policy_below)
        obj._setObject('.wf_policy_config', wfp)
    else:
        importer.logger.info(f"Set local 'wf_policy_config' of {obj.absolute_url()}")
        wf_policy = obj['.wf_policy_config']
        wf_policy.setPolicyIn(workflow_policy_in)
        wf_policy.setPolicyBelow(workflow_policy_below)

    importer.logger.info(f"Updated 'wf_policy_config' of {obj.absolute_url()}")
