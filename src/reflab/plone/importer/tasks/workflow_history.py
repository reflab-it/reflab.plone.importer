from plone.event.utils import pydt
from DateTime import DateTime
from persistent.mapping import PersistentMapping
from plone import api


def task(importer, container, data):
    obj_id = data['id']
    if not obj_id in container.objectIds():
        importer.logger.warning(f"Missing '{obj_id}' in {container.absolute_url()}")    
        return
    obj = container[obj_id]

    workflow_history = data.get('workflow_history', None)
    if not workflow_history:
        importer.logger.warning(f"Missing 'workflow_history' for {obj.absolute_url()}")
        return

    # TODO - Why this fix?
    for wf_data in workflow_history.values():
        for status in wf_data:
            status_time = status['time']
            if status_time:
                status['time'] = pydt(DateTime(status_time[:-11]))

    obj.workflow_history = PersistentMapping(workflow_history)

    wf_tool = api.portal.get_tool('portal_workflow')
    for wf in wf_tool.getWorkflowsFor(obj):
        wf.updateRoleMappingsFor(obj)

    importer.logger.info(f"Updated workflow history and permissions of {obj.absolute_url()}")