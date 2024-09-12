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

from openstack import resource


class Quota(resource.Resource):
    resource_key = 'quota'
    resources_key = 'quotas'
    base_path = '/quotas'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Flag to check the quota usage before setting the new limit. *Type: bool*
    check_limit = resource.Body('check_limit', type=bool)
    #: The maximum amount of floating IPs you can have. *Type: int*
    floating_ips = resource.Body('floatingip', type=int)
    #: The maximum amount of health monitors you can create. *Type: int*
    health_monitors = resource.Body('healthmonitor', type=int)
    #: The maximum amount of listeners you can create. *Type: int*
    listeners = resource.Body('listener', type=int)
    #: The maximum amount of load balancers you can create. *Type: int*
    load_balancers = resource.Body('loadbalancer', type=int)
    #: The maximum amount of L7 policies you can create. *Type: int*
    l7_policies = resource.Body('l7policy', type=int)
    #: The maximum amount of networks you can create. *Type: int*
    networks = resource.Body('network', type=int)
    #: The maximum amount of pools you can create. *Type: int*
    pools = resource.Body('pool', type=int)
    #: The maximum amount of ports you can create. *Type: int*
    ports = resource.Body('port', type=int)
    #: The ID of the project these quota values are for.
    project_id = resource.Body('tenant_id', alternate_id=True)
    #: The maximum amount of RBAC policies you can create. *Type: int*
    rbac_policies = resource.Body('rbac_policy', type=int)
    #: The maximum amount of routers you can create. *Type: int*
    routers = resource.Body('router', type=int)
    #: The maximum amount of subnets you can create. *Type: int*
    subnets = resource.Body('subnet', type=int)
    #: The maximum amount of subnet pools you can create. *Type: int*
    subnet_pools = resource.Body('subnetpool', type=int)
    #: The maximum amount of security group rules you can create. *Type: int*
    security_group_rules = resource.Body('security_group_rule', type=int)
    #: The maximum amount of security groups you can create. *Type: int*
    security_groups = resource.Body('security_group', type=int)

    def _prepare_request(
        self,
        requires_id=True,
        prepend_key=False,
        patch=False,
        base_path=None,
        *args,
        **kwargs,
    ):
        _request = super()._prepare_request(requires_id, prepend_key)
        if self.resource_key in _request.body:
            _body = _request.body[self.resource_key]
        else:
            _body = _request.body
        if 'id' in _body:
            del _body['id']
        return _request


class QuotaDefault(Quota):
    base_path = '/quotas/%(project)s/default'

    # capabilities
    allow_retrieve = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    # Properties
    #: The ID of the project.
    project = resource.URI('project')


class QuotaDetails(Quota):
    base_path = '/quotas/%(project)s/details'

    # capabilities
    allow_retrieve = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    # Properties
    #: The ID of the project.
    project = resource.URI('project')
    #: The maximum amount of floating IPs you can have. *Type: dict*
    floating_ips = resource.Body('floatingip', type=dict)
    #: The maximum amount of health monitors you can create. *Type: dict*
    health_monitors = resource.Body('healthmonitor', type=dict)
    #: The maximum amount of listeners you can create. *Type: dict*
    listeners = resource.Body('listener', type=dict)
    #: The maximum amount of load balancers you can create. *Type: dict*
    load_balancers = resource.Body('loadbalancer', type=dict)
    #: The maximum amount of L7 policies you can create. *Type: dict*
    l7_policies = resource.Body('l7policy', type=dict)
    #: The maximum amount of networks you can create. *Type: dict*
    networks = resource.Body('network', type=dict)
    #: The maximum amount of pools you can create. *Type: dict*
    pools = resource.Body('pool', type=dict)
    #: The maximum amount of ports you can create. *Type: dict*
    ports = resource.Body('port', type=dict)
    #: The ID of the project these quota values are for.
    project_id = resource.Body('project_id', alternate_id=True)
    #: The maximum amount of RBAC policies you can create. *Type: dict*
    rbac_policies = resource.Body('rbac_policy', type=dict)
    #: The maximum amount of routers you can create. *Type: int*
    routers = resource.Body('router', type=dict)
    #: The maximum amount of subnets you can create. *Type: dict*
    subnets = resource.Body('subnet', type=dict)
    #: The maximum amount of subnet pools you can create. *Type: dict*
    subnet_pools = resource.Body('subnetpool', type=dict)
    #: The maximum amount of security group rules you can create. *Type: dict*
    security_group_rules = resource.Body('security_group_rule', type=dict)
    #: The maximum amount of security groups you can create. *Type: dict*
    security_groups = resource.Body('security_group', type=dict)
