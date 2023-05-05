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


class StoragePool(resource.Resource):
    resources_key = "pools"
    base_path = "/scheduler-stats/pools"

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters(
        'pool',
        'backend',
        'host',
        'capabilities',
        'share_type',
    )

    #: Properties
    #: The name of the back end.
    backend = resource.Body("backend", type=str)
    #: The host of the back end.
    host = resource.Body("host", type=str)
    #: The pool for the back end
    pool = resource.Body("pool", type=str)
    #: The back end capabilities.
    capabilities = resource.Body("capabilities", type=dict)
