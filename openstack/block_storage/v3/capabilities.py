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


class Capabilities(resource.Resource):
    base_path = "/capabilities"

    # Capabilities
    allow_fetch = True

    #: Properties
    #: The capabilities description
    description = resource.Body("description")
    #: The name of volume backend capabilities.
    display_name = resource.Body("display_name")
    #: The driver version.
    driver_version = resource.Body("driver_version")
    #: The storage namespace, such as OS::Storage::Capabilities::foo.
    namespace = resource.Body("namespace")
    #: The name of the storage pool.
    pool_name = resource.Body("pool_name")
    #: The backend volume capabilites list, which consists of cinder
    #: standard capabilities and vendor unique properties.
    properties = resource.Body("properties", type=dict)
    #: A list of volume backends used to replicate volumes on this backend.
    replication_targets = resource.Body("replication_targets", type=list)
    #: The storage backend for the backend volume.
    storage_protocol = resource.Body("storage_protocol")
    #: The name of the vendor.
    vendor_name = resource.Body("vendor_name")
    #: The volume type access.
    visibility = resource.Body("visibility")
    #: The name of the back-end volume.
    volume_backend_name = resource.Body("volume_backend_name")
