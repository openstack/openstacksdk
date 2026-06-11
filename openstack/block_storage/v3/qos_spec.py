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

from collections.abc import Iterable
from typing import Any

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class QoSSpec(resource.Resource):
    resource_key = "qos_specs"
    resources_key = "qos_specs"
    base_path = "/qos-specs"

    _query_mapping = resource.QueryParameters(
        "project_id",
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    consumer = resource.Body("consumer")
    id = resource.Body("id", type=str)
    name = resource.Body("name")
    specs = resource.Body("specs")

    def associate(self, session: adapter.Adapter, vol_type_id: str) -> None:
        """Associate this QoS spec with a volume type.

        :param session: The session to use for making this request.
        :param vol_type_id: The ID of the volume type to associate with.
        """
        url = utils.urljoin(self.base_path, self.id, 'associate')
        resp = session.get(url, params={'vol_type_id': vol_type_id})
        exceptions.raise_from_response(resp)

    def disassociate(self, session: adapter.Adapter, vol_type_id: str) -> None:
        """Disassociate this QoS spec from a volume type.

        :param session: The session to use for making this request.
        :param vol_type_id: The ID of the volume type to disassociate from.
        """
        url = utils.urljoin(self.base_path, self.id, 'disassociate')
        resp = session.get(url, params={'vol_type_id': vol_type_id})
        exceptions.raise_from_response(resp)

    def disassociate_all(self, session: adapter.Adapter) -> None:
        """Disassociate this QoS spec from all volume types.

        :param session: The session to use for making this request.
        """
        url = utils.urljoin(self.base_path, self.id, 'disassociate_all')
        resp = session.get(url)
        exceptions.raise_from_response(resp)

    def delete_keys(
        self, session: adapter.Adapter, keys: Iterable[Any]
    ) -> None:
        """Delete keys from this QoS spec.

        :param session: The session to use for making this request.
        :param keys: The keys to delete.
        """
        url = utils.urljoin(self.base_path, self.id, 'delete_keys')
        resp = session.put(url, json={'keys': keys})
        exceptions.raise_from_response(resp)


class QoSSpecAssociation(resource.Resource):
    resources_key = "qos_associations"
    base_path = "/qos-specs/%(qos_spec_id)s/associations"

    # capabilities
    allow_list = True

    # Properties
    #: The type of association (e.g. "volume_type").
    association_type = resource.Body("association_type")
    #: The ID of the associated resource.
    id = resource.Body("id", type=str)
    #: The name of the associated resource.
    name = resource.Body("name")
    #: The ID of the QoS spec.
    qos_spec_id = resource.URI("qos_spec_id")
