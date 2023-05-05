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


class ClusterCertificate(resource.Resource):
    base_path = '/certificates'

    # capabilities
    allow_create = True
    allow_list = False
    allow_fetch = True

    #: The UUID of the bay.
    bay_uuid = resource.Body('bay_uuid')
    #: The UUID of the cluster.
    cluster_uuid = resource.Body('cluster_uuid', alternate_id=True)
    #: Certificate Signing Request (CSR) for authenticating client key.
    csr = resource.Body('csr')
    #: CA certificate for the bay/cluster.
    pem = resource.Body('pem')
