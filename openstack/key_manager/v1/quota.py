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
    resource_key = 'quotas'
    resources_key = 'quotas'
    base_path = '/quotas'

    # capabilities
    allow_fetch = True

    # Properties
    #: Contains the effective quota value of the current project for the
    #: secret resource.
    secrets = resource.Body("secrets")
    #: Contains the effective quota value of the current project for the
    #: orders resource.
    orders = resource.Body("orders")
    #: Contains the effective quota value of the current project for the
    #: containers resource.
    containers = resource.Body("containers")
    #: Contains the effective quota value of the current project for the
    #: consumers resource.
    consumers = resource.Body("consumers")
    #: Contains the effective quota value of the current project for the
    #: CAs resource.
    cas = resource.Body("cas")
