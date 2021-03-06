import json
import logging

from openstack_dashboard.api import heat

from openstack_dashboard.dashboards.project.stacks import mappings
from openstack_dashboard.dashboards.project.stacks import sro


LOG = logging.getLogger(__name__)


class Stack(object):
    pass


def d3_data(request, stack_id=''):
    try:
        stack = heat.stack_get(request, stack_id)
    except Exception:
        stack = Stack()
        stack.id = stack_id
        stack.stack_name = request.session.get('stack_name', '')
        stack.stack_status = 'DELETE_COMPLETE'
        stack.stack_status_reason = 'DELETE_COMPLETE'

    try:
        resources = heat.resources_list(request, stack.stack_name)
    except Exception:
        resources = []

    d3_data = {"nodes": [], "stack": {}}
    if stack:
        stack_image = mappings.get_resource_image(stack.stack_status, 'stack')
        stack_node = {
            'stack_id': stack.id,
            'name': stack.stack_name,
            'status': stack.stack_status,
            'image': stack_image,
            'image_size': 60,
            'image_x': -30,
            'image_y': -30,
            'text_x': 40,
            'text_y': ".35em",
            'in_progress': True if (mappings.get_resource_status(
                                    stack.stack_status) ==
                                   'IN_PROGRESS') else False,
            'info_box': sro.stack_info(stack, stack_image)
        }
        d3_data['stack'] = stack_node

    if resources:
        for resource in resources:
            resource_image = mappings.get_resource_image(
                resource.resource_status,
                resource.resource_type)
            resource_status = mappings.get_resource_status(
                resource.resource_status)
            if resource_status in ('IN_PROGRESS', 'INIT'):
                in_progress = True
            else:
                in_progress = False
            resource_node = {
                'name': resource.resource_name,
                'status': resource.resource_status,
                'image': resource_image,
                'required_by': resource.required_by,
                'image_size': 50,
                'image_x': -25,
                'image_y': -25,
                'text_x': 35,
                'text_y': ".35em",
                'in_progress': in_progress,
                'info_box': sro.resource_info(resource)
            }
            d3_data['nodes'].append(resource_node)
    return json.dumps(d3_data)
