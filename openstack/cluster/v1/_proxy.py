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

from openstack.cluster.v1 import action
from openstack.cluster.v1 import build_info
from openstack.cluster.v1 import cluster
from openstack.cluster.v1 import node
from openstack.cluster.v1 import policy
from openstack.cluster.v1 import profile
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def get_build_info(self):
        """Get build info for service engine and API

        :returns: A dictionary containing the API and engine revision string.
        """
        return self._get(build_info.BuildInfo)

    def create_profile(self, **attrs):
        """Create a new profile from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.profile.Profile`, it is comprised
             of the properties on the Profile class.

        :returns: The results of profile creation.
        :rtype: :class:`~openstack.cluster.v1.profile.Profile`.
        """
        return self._create(profile.Profile, **attrs)

    def delete_profile(self, value, ignore_missing=True):
        """Delete a profile.

        :param value: The value can be either the name or ID of a profile or a
            :class:`~openstack.cluster.v1.profile.Profile` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the profile could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent profile.

        :returns: ``None``
        """
        self._delete(profile.Profile, value, ignore_missing=ignore_missing)

    def find_profile(self, name_or_id, ignore_missing=True):
        """Find a single profile.

        :param str name_or_id: The name or ID of a profile.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.cluster.v1.profile.Profile` object
            or None
        """
        return self._find(profile.Profile, name_or_id,
                          ignore_missing=ignore_missing)

    def get_profile(self, value):
        """Get a single profile.

        :param value: The value can be the name or ID of a profile or a
            :class:`~openstack.cluster.v1.profile.Profile` instance.

        :returns: One :class:`~openstack.cluster.v1.profile.Profile`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            profile matching the criteria could be found.
        """
        return self._get(profile.Profile, value)

    def profiles(self, **query):
        """Retrieve a generator of profiles.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the profiles to be returned. Available parameters include:

            * show_deleted: A boolean value indicating whether soft-deleted
                profiles should be returned as well.
            * filters: A list of key-value pairs for Senlin server to determine
                whether a profile should be included in the list result.
            * sort_keys: A list of key names for sorting the resulted list.
            * sort_dir: Direction for sorting, and its valid values are 'asc'
                and 'desc'.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of profile instances.
        """
        return self._list(profile.Profile, paginated=True, **query)

    def update_profile(self, value, **attrs):
        """Update a profile.

        :param value: Either the name or the ID of the profile, or an instance
            of :class:`~openstack.cluster.v1.profile.Profile`.
        :param attrs: The attributes to update on the profile represented by
            the ``value`` parameter.

        :returns: The updated profile.
        :rtype: :class:`~openstack.cluster.v1.profile.Profile`
        """
        return self._update(profile.Profile, value, **attrs)

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

        :param str name_or_id: The name or ID of a cluster.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.cluster.v1.cluster.Cluster` object
            or None
        """
        return self._find(cluster.Cluster, name_or_id,
                          ignore_missing=ignore_missing)

    def get_cluster(self, value):
        """Get a single cluster.

        :param value: The value can be the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.

        :returns: One :class:`~openstack.cluster.v1.cluster.Cluster`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            cluster matching the criteria could be found.
        """
        return self._get(cluster.Cluster, value)

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
                and 'desc'.
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

    def create_node(self, **attrs):
        """Create a new node from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.node.Node`, it is comprised
             of the properties on the Node class.

        :returns: The results of node creation.
        :rtype: :class:`~openstack.cluster.v1.node.Node`.
        """
        return self._create(node.Node, **attrs)

    def delete_node(self, value, ignore_missing=True):
        """Delete a node.

        :param value: The value can be either the name or ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the node could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent node.

        :returns: ``None``
        """
        self._delete(node.Node, value, ignore_missing=ignore_missing)

    def find_node(self, name_or_id, ignore_missing=True):
        """Find a single node.

        :param str name_or_id: The name or ID of a node.
        :returns: One :class:`~openstack.cluster.v1.node.Node` object or None.
        """
        return self._find(node.Node, name_or_id, ignore_missing=ignore_missing)

    def get_node(self, value):
        """Get a single node.

        :param value: The value can be the name or ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.

        :returns: One :class:`~openstack.cluster.v1.node.Node`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            node matching the name or ID could be found.
        """
        return self._get(node.Node, value)

    def nodes(self, **query):
        """Retrieve a generator of nodes.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the nodes to be returned. Available parameters include:

            * cluster_id: A string including the name or ID of a cluster to
                which the resulted node(s) is a member.
            * show_deleted: A boolean value indicating whether soft-deleted
                nodes should be returned as well.
            * filters: A list of key-value pairs for server to determine
                whether a node should be included in the list result.
            * sort_keys: A list of key names for sorting the resulted list.
            * sort_dir: Direction for sorting, and its valid values are 'asc'
                and 'desc'.
            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen node. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen node from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of node instances.
        """
        return self._list(node.Node, paginated=True, **query)

    def update_node(self, value, **attrs):
        """Update a node.

        :param value: Either the name or the ID of the node, or an instance
            of :class:`~openstack.cluster.v1.node.Node`.
        :param attrs: The attributes to update on the node represented by
            the ``value`` parameter.

        :returns: The updated node.
        :rtype: :class:`~openstack.cluster.v1.node.Node`
        """
        return self._update(node.Node, value, **attrs)

    def create_policy(self, **attrs):
        """Create a new policy from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.policy.Policy`, it is comprised
             of the properties on the Policy class.

        :returns: The results of policy creation.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`.
        """
        return self._create(policy.Policy, **attrs)

    def delete_policy(self, value, ignore_missing=True):
        """Delete a policy.

        :param value: The value can be either the name or ID of a policy or a
            :class:`~openstack.cluster.v1.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the policy could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent policy.

        :returns: ``None``
        """
        self._delete(policy.Policy, value, ignore_missing=ignore_missing)

    def find_policy(self, name_or_id, ignore_missing=True):
        """Find a single policy.

        :param str name_or_id: The name or ID of a policy.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the specified policy does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent policy.
        :returns: A policy object or None.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`
        """
        return self._find(policy.Policy, name_or_id,
                          ignore_missing=ignore_missing)

    def get_policy(self, value):
        """Get a single policy.

        :param value: The value can be the name or ID of a policy or a
            :class:`~openstack.cluster.v1.policy.Policy` instance.

        :returns: A policy object.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            policy matching the criteria could be found.
        """
        return self._get(policy.Policy, value)

    def policies(self, **query):
        """Retrieve a generator of policies.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the policies to be returned. Available parameters include:

            * name: The name of a policy object.
            * type: The type name of policy objects.
            * level: The enforcement level of policy objects.
            * cooldown: The default cooldown value of a policy object.
            * show_deleted: A boolean value indicating whether soft-deleted
                policies should be returned as well.
        :returns: A generator of policy instances.
        """
        return self._list(policy.Policy, paginated=True, **query)

    def update_policy(self, value, **attrs):
        """Update a policy.

        :param value: Either the name or the ID of a policy, or an instance
            of :class:`~openstack.cluster.v1.policy.Policy`.
        :param attrs: The attributes to update on the policy represented by
            the ``value`` parameter.

        :returns: The updated policy.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`
        """
        return self._update(policy.Policy, value, **attrs)

    def get_action(self, value):
        """Get a single action.

        :param value: The value can be the name or ID of an action or a
            :class:`~openstack.cluster.v1.action.Action` instance.

        :returns: an action object.
        :rtype: :class:`~openstack.cluster.v1.action.Action`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            action matching the criteria could be found.
        """
        return self._get(action.Action, value)

    def actions(self, **query):
        """Retrieve a generator of actions.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the actions to be returned. Available parameters include:

            * name: name of action for query.
            * target: ID of the target object for which the actions should be
                returned.
            * action: built-in action types for query.
            * show_deleted: A boolean value indicating whether soft-deleted
                actions should be returned as well.
            * sort_keys: A list of key names for sorting the resulted list.
            * sort_dir: Direction for sorting, and its valid values are 'asc'
                and 'desc'.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of action instances.
        """
        return self._list(action.Action, paginated=True, **query)
