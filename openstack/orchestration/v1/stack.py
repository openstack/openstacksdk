# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import exceptions
from openstack import format
from openstack.orchestration import orchestration_service
from openstack import resource
from openstack import utils


class Stack(resource.Resource):
    name_attribute = 'stack_name'
    resource_key = 'stack'
    resources_key = 'stacks'
    base_path = '/stacks'
    service = orchestration_service.OrchestrationService()

    # capabilities
    # NOTE(thowe): Special handling for other operations
    allow_create = True
    allow_list = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True

    # Properties
    #: Placeholder for AWS compatible template listing capabilities
    #: required by the stack.
    capabilities = resource.prop('capabilities')
    #: Timestamp of the stack creation.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('creation_time', type=format.ISO8601)
    #: A text description of the stack.
    description = resource.prop('description')
    #: Whether the stack will support a rollback operation on stack
    #: create/update failures. *Type: bool*
    is_rollback_disabled = resource.prop('disable_rollback', type=bool)
    #: A list of dictionaries containing links relevant to the stack.
    links = resource.prop('links')
    #: Name of the stack.
    name = resource.prop('stack_name')
    #: Placeholder for future extensions where stack related events
    #: can be published.
    notification_topics = resource.prop('notification_topics')
    #: A dictionary containing output keys and values from the stack, if any.
    outputs = resource.prop('outputs')
    #: A dictionary containing the parameter names and values for the stack.
    parameters = resource.prop('parameters', type=dict)
    #: A string representation of the stack status, e.g. ``CREATE_COMPLETED``.
    status = resource.prop('stack_status')
    #: A text explaining how the stack transits to its current status.
    status_reason = resource.prop('stack_status_reason')
    #: Stack template description text. Currently contains the same text
    #: as that of the ``description`` property.
    template_description = resource.prop('template_description')
    #: A URL (i.e. HTTP or HTTPS) where stack template can be retrieved.
    template_url = resource.prop('template_url')
    #: Stack operation timeout in minutes.
    timeout_mins = resource.prop('timeout_mins')
    #: Timestamp of last update on the stack.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_time', type=format.ISO8601)

    def _action(self, session, body):
        """Perform stack actions"""
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def check(self, session):
        return self._action(session, {'check': ''})

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None, path_args=None):
        body = attrs.copy()
        body.pop('id', None)
        body.pop('name', None)
        url = cls.base_path
        resp = session.post(url, endpoint_filter=cls.service, json=body)
        resp = resp.json()
        return resp[cls.resource_key]

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        # Heat returns a 202 for update operation, we ignore the non-existent
        # response.body and do an additional get
        body = attrs.copy()
        body.pop('id', None)
        body.pop('name', None)
        url = cls._get_url(path_args, resource_id)
        session.put(url, endpoint_filter=cls.service, json=body)
        return cls.get_by_id(session, resource_id)

    @classmethod
    def find(cls, session, name_or_id, path_args=None, ignore_missing=True):
        stk = super(Stack, cls).find(session, name_or_id, path_args=path_args,
                                     ignore_missing=ignore_missing)
        if stk and stk.status in ['DELETE_COMPLETE', 'ADOPT_COMPLETE']:
            if ignore_missing:
                return None
            else:
                raise exceptions.ResourceNotFound(
                    "No stack found for %s" % name_or_id)
        return stk

    def get(self, session, include_headers=False, args=None):
        stk = super(Stack, self).get(session, include_headers, args)
        if stk and stk.status in ['DELETE_COMPLETE', 'ADOPT_COMPLETE']:
            raise exceptions.NotFoundException(
                "No stack found for %s" % stk.id)
        return stk


class StackPreview(Stack):
    base_path = '/stacks/preview'

    allow_create = True
    allow_list = False
    allow_retrieve = False
    allow_update = False
    allow_delete = False
