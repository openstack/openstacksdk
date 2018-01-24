# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.clustering import clustering_service
from openstack import resource


class ClusterAttr(resource.Resource):
    resources_key = 'cluster_attributes'
    base_path = '/clusters/%(cluster_id)s/attrs/%(path)s'
    service = clustering_service.ClusteringService()

    # capabilities
    allow_list = True

    # Properties
    #: The identity of the cluster
    cluster_id = resource.URI('cluster_id')
    #: The json path string for attribute retrieval
    path = resource.URI('path')
    #: The id of the node that carries the attribute value.
    node_id = resource.Body('id')
    #: The value of the attribute requested.
    attr_value = resource.Body('value')
