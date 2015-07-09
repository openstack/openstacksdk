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

from openstack.cluster.v1 import cluster
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_cluster(self, **attrs):
        """Create a new cluster from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.cluster.Cluster`, it is comprised
             of the properties on the Cluster class.

        :returns: The results of cluster creation.
        :rtype: :class:`~openstack.cluster.v1.cluster.Cluster`.
        """
        return self._create(cluster.Cluster, **attrs)

    def delete_cluster(self, value, ignore_missing=True):
        """Delete a cluster.

        :param value: The value can be either the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent cluster.

        :returns: ``None``
        """
        self._delete(cluster.Cluster, value, ignore_missing=ignore_missing)

    def find_cluster(self, name_or_id, ignore_missing=True):
        """Find a single cluster.

        :param name_or_id: The name or ID of a cluster.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.cluster.v1.cluster.Cluster` object
            or None
        """
        return cluster.Cluster.find(self.session, name_or_id,
                                    ignore_missing=ignore_missing)

    def get_cluster(self, name_or_id):
        """Get a single cluster.

        :param name_or_id: The value can be the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.

        :returns: One :class:`~openstack.cluster.v1.cluster.Cluster`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            cluster matching the criteria could be found.
        """
        return self._get(cluster.Cluster, name_or_id)

    def clusters(self, **query):
        """Retrieve a generator of clusters.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the clusters to be returned. Available parameters include:

            * show_deleted: A boolean value indicating whether soft-deleted
                clusters should be returned as well.
            * filters: A list of key-value pairs for Senlin server to determine
                whether a cluster should be included in the list result.
            * sort_keys: A list of key names for sorting the resulted list.
            * sort_dir: Direction for sorting, and its valid values are 'asc'
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of cluster instances.
        """
        return self._list(cluster.Cluster, paginated=True, **query)

    def update_cluster(self, value, **attrs):
        """Update a cluster.

        :param value: Either the name or the ID of the cluster, or an instance
            of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param attrs: The attributes to update on the cluster represented by
            the ``value`` parameter.

        :returns: The updated cluster.
        :rtype: :class:`~openstack.cluster.v1.cluster.Cluster`
        """
        return self._update(cluster.Cluster, value, **attrs)
