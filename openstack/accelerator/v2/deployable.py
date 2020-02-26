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
from openstack import resource


class Deployable(resource.Resource):
    resource_key = 'deployable'
    resources_key = 'deployables'
    base_path = '/deployables'
    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_patch = True
    #: The timestamp when this deployable was created.
    created_at = resource.Body('created_at')
    #: The device_id of the deployable.
    device_id = resource.Body('device_id')
    #: The UUID of the deployable.
    id = resource.Body('uuid', alternate_id=True)
    #: The name of the deployable.
    name = resource.Body('name')
    #: The num_accelerator of the deployable.
    num_accelerators = resource.Body('num_accelerators')
    #: The parent_id of the deployable.
    parent_id = resource.Body('parent_id')
    #: The root_id of the deployable.
    root_id = resource.Body('root_id')
    #: The timestamp when this deployable was updated.
    updated_at = resource.Body('updated_at')

    def _commit(self, session, request, method, microversion, has_body=True,
                retry_on_conflict=None):
        session = self._get_session(session)
        kwargs = {}
        retriable_status_codes = set(session.retriable_status_codes or ())
        if retry_on_conflict:
            kwargs['retriable_status_codes'] = retriable_status_codes | {409}
        elif retry_on_conflict is not None and retriable_status_codes:
            # The baremetal proxy defaults to retrying on conflict, allow
            # overriding it via an explicit retry_on_conflict=False.
            kwargs['retriable_status_codes'] = retriable_status_codes - {409}
        try:
            call = getattr(session, method.lower())
        except AttributeError:
            raise exceptions.ResourceFailure(
                msg="Invalid commit method: %s" % method)
        request.url = request.url + "/program"
        response = call(request.url, json=request.body,
                        headers=request.headers, microversion=microversion,
                        **kwargs)
        self.microversion = microversion
        self._translate_response(response, has_body=has_body)
        return self
