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


class ProjectQuota(resource.Resource):
    resource_key = 'project_quotas'
    resources_key = 'project_quotas'
    base_path = '/project-quotas'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Contains the configured quota value of the requested project for the
    #: secret resource.
    secrets = resource.Body("secrets")
    #: Contains the configured quota value of the requested project for the
    #: orders resource.
    orders = resource.Body("orders")
    #: Contains the configured quota value of the requested project for the
    #: containers resource.
    containers = resource.Body("containers")
    #: Contains the configured quota value of the requested project for the
    #: consumers resource.
    consumers = resource.Body("consumers")
    #: Contains the configured quota value of the requested project for the CAs
    #: resource.
    cas = resource.Body("cas")
