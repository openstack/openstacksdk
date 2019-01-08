# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack import resource


class Quota(resource.Resource):
    resource_key = 'quota'
    resources_key = 'quotas'
    base_path = '/lbaas/quotas'

    # capabilities
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The maximum amount of load balancers you can have. *Type: int*
    load_balancers = resource.Body('load_balancer', type=int)
    #: The maximum amount of listeners you can create. *Type: int*
    listeners = resource.Body('listener', type=int)
    #: The maximum amount of pools you can create. *Type: int*
    pools = resource.Body('pool', type=int)
    #: The maximum amount of health monitors you can create. *Type: int*
    health_monitors = resource.Body('health_monitor', type=int)
    #: The maximum amount of members you can create. *Type: int*
    members = resource.Body('member', type=int)
    #: The ID of the project this quota is associated with.
    project_id = resource.Body('project_id', alternate_id=True)

    def _prepare_request(self, requires_id=True,
                         base_path=None, prepend_key=False):
        _request = super(Quota, self)._prepare_request(requires_id,
                                                       prepend_key,
                                                       base_path=base_path)
        if self.resource_key in _request.body:
            _body = _request.body[self.resource_key]
        else:
            _body = _request.body
        if 'id' in _body:
            del _body['id']
        return _request


class QuotaDefault(Quota):
    base_path = '/lbaas/quotas/defaults'

    allow_retrieve = True
    allow_commit = False
    allow_delete = False
    allow_list = False
