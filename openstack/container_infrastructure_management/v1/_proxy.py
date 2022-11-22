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

from openstack.container_infrastructure_management.v1 import (
    cluster as _cluster
)
from openstack import proxy


class Proxy(proxy.Proxy):

    _resource_registry = {
        "cluster": _cluster.Cluster,
    }

    def create_cluster(self, **attrs):
        """Create a new cluster from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`,
            comprised of the properties on the Cluster class.
        :returns: The results of cluster creation
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._create(_cluster.Cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete a cluster

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent cluster.
        :returns: ``None``
        """
        self._delete(_cluster.Cluster, cluster, ignore_missing=ignore_missing)

    def find_cluster(self, name_or_id, ignore_missing=True):
        """Find a single cluster

        :param name_or_id: The name or ID of a cluster.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            or None
        """
        return self._find(
            _cluster.Cluster,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_cluster(self, cluster):
        """Get a single cluster

        :param cluster: The value can be the ID of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.

        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_cluster.Cluster, cluster)

    def clusters(self, **query):
        """Return a generator of clusters

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of cluster objects
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._list(_cluster.Cluster, **query)

    def update_cluster(self, cluster, **attrs):
        """Update a cluster

        :param cluster: Either the id of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.
        :param attrs: The attributes to update on the cluster represented
            by ``cluster``.

        :returns: The updated cluster
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._update(_cluster.Cluster, cluster, **attrs)
