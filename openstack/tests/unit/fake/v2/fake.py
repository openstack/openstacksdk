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


class Fake(resource.Resource):
    resource_key = "resource"
    resources_key = "resources"
    base_path = "/fake"

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = True

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The name of this resource.
    name = resource.Body("name", alternate_id=True)
    #: The value of the resource. Also available in headers.
    value = resource.Body("value", alias="x-resource-value")
    #: Is this resource cool? If so, set it to True.
    #: This is a multi-line comment about cool stuff.
    cool = resource.Body("cool", type=bool)
