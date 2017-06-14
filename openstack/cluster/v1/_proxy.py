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

from openstack.cluster.v1 import action as _action
from openstack.cluster.v1 import build_info
from openstack.cluster.v1 import cluster as _cluster
from openstack.cluster.v1 import cluster_attr as _cluster_attr
from openstack.cluster.v1 import cluster_policy as _cluster_policy
from openstack.cluster.v1 import event as _event
from openstack.cluster.v1 import node as _node
from openstack.cluster.v1 import policy as _policy
from openstack.cluster.v1 import policy_type as _policy_type
from openstack.cluster.v1 import profile as _profile
from openstack.cluster.v1 import profile_type as _profile_type
from openstack.cluster.v1 import receiver as _receiver
from openstack.cluster.v1 import service as _service
from openstack import proxy2
from openstack import resource2
from openstack import utils


class Proxy(proxy2.BaseProxy):

    def get_build_info(self):
        """Get build info for service engine and API

        :returns: A dictionary containing the API and engine revision string.
        """
        return self._get(build_info.BuildInfo, requires_id=False)

    def profile_types(self, **query):
        """Get a generator of profile types.

        :returns: A generator of objects that are of type
                  :class:`~openstack.cluster.v1.profile_type.ProfileType`
        """
        return self._list(_profile_type.ProfileType, paginated=False, **query)

    def get_profile_type(self, profile_type):
        """Get the details about a profile_type.

        :param name: The name of the profile_type to retrieve or an object of
                    :class:`~openstack.cluster.v1.profile_type.ProfileType`.

        :returns: A :class:`~openstack.cluster.v1.profile_type.ProfileType`
                  object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            profile_type matching the name could be found.
        """
        return self._get(_profile_type.ProfileType, profile_type)

    def policy_types(self, **query):
        """Get a generator of policy types.

        :returns: A generator of objects that are of type
                  :class:`~openstack.cluster.v1.policy_type.PolicyType`
        """
        return self._list(_policy_type.PolicyType, paginated=False, **query)

    def get_policy_type(self, policy_type):
        """Get the details about a policy_type.

        :param policy_type: The name of a poicy_type or an object of
                :class:`~openstack.cluster.v1.policy_type.PolicyType`.

        :returns: A :class:`~openstack.cluster.v1.policy_type.PolicyType`
                  object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            policy_type matching the name could be found.
        """
        return self._get(_policy_type.PolicyType, policy_type)

    def create_profile(self, **attrs):
        """Create a new profile from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.profile.Profile`, it is comprised
             of the properties on the Profile class.

        :returns: The results of profile creation.
        :rtype: :class:`~openstack.cluster.v1.profile.Profile`.
        """
        return self._create(_profile.Profile, **attrs)

    def delete_profile(self, profile, ignore_missing=True):
        """Delete a profile.

        :param profile: The value can be either the name or ID of a profile or
            a :class:`~openstack.cluster.v1.profile.Profile` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the profile could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent profile.

        :returns: ``None``
        """
        self._delete(_profile.Profile, profile, ignore_missing=ignore_missing)

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
        return self._find(_profile.Profile, name_or_id,
                          ignore_missing=ignore_missing)

    def get_profile(self, profile):
        """Get a single profile.

        :param profile: The value can be the name or ID of a profile or a
            :class:`~openstack.cluster.v1.profile.Profile` instance.

        :returns: One :class:`~openstack.cluster.v1.profile.Profile`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            profile matching the criteria could be found.
        """
        return self._get(_profile.Profile, profile)

    def profiles(self, **query):
        """Retrieve a generator of profiles.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the profiles to be returned. Available parameters include:

            * name: The name of a profile.
            * type: The type name of a profile.
            * metadata: A list of key-value pairs that are associated with a
                profile.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.
            * global_project: A boolean value indicating whether profiles
                from all projects will be returned.

        :returns: A generator of profile instances.
        """
        return self._list(_profile.Profile, paginated=True, **query)

    def update_profile(self, profile, **attrs):
        """Update a profile.

        :param profile: Either the name or the ID of the profile, or an
            instance of :class:`~openstack.cluster.v1.profile.Profile`.
        :param attrs: The attributes to update on the profile represented by
            the ``value`` parameter.

        :returns: The updated profile.
        :rtype: :class:`~openstack.cluster.v1.profile.Profile`
        """
        return self._update(_profile.Profile, profile, **attrs)

    def validate_profile(self, **attrs):
        """Validate a profile spec.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.profile.ProfileValidate`, it is
             comprised of the properties on the Profile class.

        :returns: The results of profile validation.
        :rtype: :class:`~openstack.cluster.v1.profile.ProfileValidate`.
        """
        return self._create(_profile.ProfileValidate, **attrs)

    def create_cluster(self, **attrs):
        """Create a new cluster from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.cluster.Cluster`, it is comprised
             of the properties on the Cluster class.

        :returns: The results of cluster creation.
        :rtype: :class:`~openstack.cluster.v1.cluster.Cluster`.
        """
        return self._create(_cluster.Cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete a cluster.

        :param cluster: The value can be either the name or ID of a cluster or
            a :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent cluster.

        :returns: The instance of the Cluster which was deleted.
        :rtype: :class:`~openstack.cluster.v1.cluster.Cluster`.
        """
        return self._delete(_cluster.Cluster, cluster,
                            ignore_missing=ignore_missing)

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
        return self._find(_cluster.Cluster, name_or_id,
                          ignore_missing=ignore_missing)

    def get_cluster(self, cluster):
        """Get a single cluster.

        :param cluster: The value can be the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.

        :returns: One :class:`~openstack.cluster.v1.cluster.Cluster`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            cluster matching the criteria could be found.
        """
        return self._get(_cluster.Cluster, cluster)

    def clusters(self, **query):
        """Retrieve a generator of clusters.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the clusters to be returned. Available parameters include:

            * name: The name of a cluster.
            * status: The current status of a cluster.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.
            * global_project: A boolean value indicating whether clusters
                from all projects will be returned.

        :returns: A generator of cluster instances.
        """
        return self._list(_cluster.Cluster, paginated=True, **query)

    def update_cluster(self, cluster, **attrs):
        """Update a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param attrs: The attributes to update on the cluster represented by
            the ``cluster`` parameter.

        :returns: The updated cluster.
        :rtype: :class:`~openstack.cluster.v1.cluster.Cluster`
        """
        return self._update(_cluster.Cluster, cluster, **attrs)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use add_nodes_to_cluster instead")
    def cluster_add_nodes(self, cluster, nodes):
        """Add nodes to a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be added to the cluster.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.add_nodes_to_cluster(cluster, nodes)

    def add_nodes_to_cluster(self, cluster, nodes):
        """Add nodes to a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be added to the cluster.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.add_nodes(self._session, nodes)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use remove_nodes_from_cluster instead")
    def cluster_del_nodes(self, cluster, nodes, **params):
        """Remove nodes from a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be removed from the cluster.
        :param kwargs \*\*params: Optional query parameters to be sent to
            restrict the nodes to be returned. Available parameters include:

            * destroy_after_deletion: A boolean value indicating whether the
                                      deleted nodes to be destroyed right away.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.remove_nodes_from_cluster(cluster, nodes, **params)

    def remove_nodes_from_cluster(self, cluster, nodes, **params):
        """Remove nodes from a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be removed from the cluster.
        :param kwargs \*\*params: Optional query parameters to be sent to
            restrict the nodes to be returned. Available parameters include:

            * destroy_after_deletion: A boolean value indicating whether the
                                      deleted nodes to be destroyed right away.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.del_nodes(self._session, nodes, **params)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use replace_nodes_in_cluster instead")
    def cluster_replace_nodes(self, cluster, nodes):
        """Replace the nodes in a cluster with specified nodes.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be deleted/added to the cluster.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.replace_nodes_in_cluster(cluster, nodes)

    def replace_nodes_in_cluster(self, cluster, nodes):
        """Replace the nodes in a cluster with specified nodes.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param nodes: List of nodes to be deleted/added to the cluster.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.replace_nodes(self._session, nodes)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use scale_out_cluster instead")
    def cluster_scale_out(self, cluster, count=None):
        """Inflate the size of a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param count: Optional parameter specifying the number of nodes to
            be added.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.scale_out_cluster(cluster, count)

    def scale_out_cluster(self, cluster, count=None):
        """Inflate the size of a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param count: Optional parameter specifying the number of nodes to
            be added.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.scale_out(self._session, count)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use scale_in_cluster instead")
    def cluster_scale_in(self, cluster, count=None):
        """Shrink the size of a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param count: Optional parameter specifying the number of nodes to
            be removed.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.scale_in_cluster(cluster, count)

    def scale_in_cluster(self, cluster, count=None):
        """Shrink the size of a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param count: Optional parameter specifying the number of nodes to
            be removed.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.scale_in(self._session, count)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use resize_cluster instead")
    def cluster_resize(self, cluster, **params):
        """Resize of cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param dict \*\*params: A dictionary providing the parameters for the
            resize action.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.resize_cluster(cluster, **params)

    def resize_cluster(self, cluster, **params):
        """Resize of cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param dict \*\*params: A dictionary providing the parameters for the
            resize action.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.resize(self._session, **params)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use attach_policy_to_cluster instead")
    def cluster_attach_policy(self, cluster, policy, **params):
        """Attach a policy to a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :param dict \*\*params: A dictionary containing the properties for the
            policy to be attached.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.attach_policy_to_cluster(cluster, policy, **params)

    def attach_policy_to_cluster(self, cluster, policy, **params):
        """Attach a policy to a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :param dict \*\*params: A dictionary containing the properties for the
            policy to be attached.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.policy_attach(self._session, policy, **params)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use detach_policy_from_cluster instead")
    def cluster_detach_policy(self, cluster, policy):
        """Attach a policy to a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.detach_policy_from_cluster(cluster, policy)

    def detach_policy_from_cluster(self, cluster, policy):
        """Detach a policy from a cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.policy_detach(self._session, policy)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use update_cluster_policy instead")
    def cluster_update_policy(self, cluster, policy, **params):
        """Change properties of a policy which is bound to the cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :param dict \*\*params: A dictionary containing the new properties for
            the policy.
        :returns: A dict containing the action initiated by this operation.
        """
        return self.update_cluster_policy(cluster, policy, **params)

    def update_cluster_policy(self, cluster, policy, **params):
        """Change properties of a policy which is bound to the cluster.

        :param cluster: Either the name or the ID of the cluster, or an
            instance of :class:`~openstack.cluster.v1.cluster.Cluster`.
        :param policy: Either the name or the ID of a policy.
        :param dict \*\*params: A dictionary containing the new properties for
            the policy.
        :returns: A dict containing the action initiated by this operation.
        """
        if isinstance(cluster, _cluster.Cluster):
            obj = cluster
        else:
            obj = self._find(_cluster.Cluster, cluster, ignore_missing=False)
        return obj.policy_update(self._session, policy, **params)

    def collect_cluster_attrs(self, cluster, path):
        """Collect attribute values across a cluster.

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param path: A Json path string specifying the attribute to collect.

        :returns: A dictionary containing the list of attribute values.
        """
        return self._list(_cluster_attr.ClusterAttr, paginated=False,
                          cluster_id=cluster, path=path)

    def check_cluster(self, cluster, **params):
        """Check a cluster.

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param dict params: A dictionary providing the parameters for the
            check action.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_cluster.Cluster, cluster)
        return obj.check(self._session, **params)

    def recover_cluster(self, cluster, **params):
        """recover a cluster.

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param dict params: A dictionary providing the parameters for the
                            recover action.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_cluster.Cluster, cluster)
        return obj.recover(self._session, **params)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use perform_operation_on_cluster instead")
    def cluster_operation(self, cluster, operation, **params):
        """Perform an operation on the specified cluster.

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param operation: A string specifying the operation to be performed.
        :param dict params: A dictionary providing the parameters for the
                            operation.

        :returns: A dictionary containing the action ID.
        """
        return self.perform_operation_on_cluster(cluster, operation, **params)

    def perform_operation_on_cluster(self, cluster, operation, **params):
        """Perform an operation on the specified cluster.

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param operation: A string specifying the operation to be performed.
        :param dict params: A dictionary providing the parameters for the
                            operation.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_cluster.Cluster, cluster)
        return obj.op(self._session, operation, **params)

    def create_node(self, **attrs):
        """Create a new node from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.node.Node`, it is comprised
             of the properties on the ``Node`` class.

        :returns: The results of node creation.
        :rtype: :class:`~openstack.cluster.v1.node.Node`.
        """
        return self._create(_node.Node, **attrs)

    def delete_node(self, node, ignore_missing=True):
        """Delete a node.

        :param node: The value can be either the name or ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the node could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent node.

        :returns: The instance of the Node which was deleted.
        :rtype: :class:`~openstack.cluster.v1.node.Node`.
        """
        return self._delete(_node.Node, node, ignore_missing=ignore_missing)

    def find_node(self, name_or_id, ignore_missing=True):
        """Find a single node.

        :param str name_or_id: The name or ID of a node.
        :returns: One :class:`~openstack.cluster.v1.node.Node` object or None.
        """
        return self._find(_node.Node, name_or_id,
                          ignore_missing=ignore_missing)

    def get_node(self, node, details=False):
        """Get a single node.

        :param node: The value can be the name or ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param details: An optional argument that indicates whether the
            server should return more details when retrieving the node data.

        :returns: One :class:`~openstack.cluster.v1.node.Node`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            node matching the name or ID could be found.
        """
        # NOTE: When retrieving node with details (using NodeDetail resource),
        # the `node_id` is treated as part of the base_path thus a URI
        # property rather than a resource ID as assumed by the _get() method
        # in base proxy.
        if details:
            return self._get(_node.NodeDetail, requires_id=False, node_id=node)
        return self._get(_node.Node, node)

    def nodes(self, **query):
        """Retrieve a generator of nodes.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the nodes to be returned. Available parameters include:

            * cluster_id: A string including the name or ID of a cluster to
                which the resulted node(s) is a member.
            * name: The name of a node.
            * status: The current status of a node.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen node. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen node from the response as the marker parameter
                value in a subsequent limited request.
            * global_project: A boolean value indicating whether nodes
                from all projects will be returned.

        :returns: A generator of node instances.
        """
        return self._list(_node.Node, paginated=True, **query)

    def update_node(self, node, **attrs):
        """Update a node.

        :param node: Either the name or the ID of the node, or an instance
            of :class:`~openstack.cluster.v1.node.Node`.
        :param attrs: The attributes to update on the node represented by
            the ``node`` parameter.

        :returns: The updated node.
        :rtype: :class:`~openstack.cluster.v1.node.Node`
        """
        return self._update(_node.Node, node, **attrs)

    def check_node(self, node, **params):
        """Check the health of the specified node.

        :param node: The value can be either the ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param dict params: A dictionary providing the parametes to the check
                            action.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_node.Node, node)
        return obj.check(self._session, **params)

    def recover_node(self, node, **params):
        """Recover the specified node into healthy status.

        :param node: The value can be either the ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param dict params: A dict supplying parameters to the recover action.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_node.Node, node)
        return obj.recover(self._session, **params)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="Use perform_operation_on_node instead")
    def node_operation(self, node, operation, **params):
        """Perform an operation on the specified node.

        :param cluster: The value can be either the ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param operation: A string specifying the operation to be performed.
        :param dict params: A dictionary providing the parameters for the
                            operation.

        :returns: A dictionary containing the action ID.
        """
        return self.perform_operation_on_node(node, operation, **params)

    def perform_operation_on_node(self, node, operation, **params):
        """Perform an operation on the specified node.

        :param cluster: The value can be either the ID of a node or a
            :class:`~openstack.cluster.v1.node.Node` instance.
        :param operation: A string specifying the operation to be performed.
        :param dict params: A dictionary providing the parameters for the
                            operation.

        :returns: A dictionary containing the action ID.
        """
        obj = self._get_resource(_node.Node, node)
        return obj.op(self._session, operation, **params)

    def create_policy(self, **attrs):
        """Create a new policy from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.policy.Policy`, it is comprised
             of the properties on the ``Policy`` class.

        :returns: The results of policy creation.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`.
        """
        return self._create(_policy.Policy, **attrs)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete a policy.

        :param policy: The value can be either the name or ID of a policy or a
            :class:`~openstack.cluster.v1.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the policy could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent policy.

        :returns: ``None``
        """
        self._delete(_policy.Policy, policy, ignore_missing=ignore_missing)

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
        return self._find(_policy.Policy, name_or_id,
                          ignore_missing=ignore_missing)

    def get_policy(self, policy):
        """Get a single policy.

        :param policy: The value can be the name or ID of a policy or a
            :class:`~openstack.cluster.v1.policy.Policy` instance.

        :returns: A policy object.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            policy matching the criteria could be found.
        """
        return self._get(_policy.Policy, policy)

    def policies(self, **query):
        """Retrieve a generator of policies.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the policies to be returned. Available parameters include:

            * name: The name of a policy.
            * type: The type name of a policy.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.
            * global_project: A boolean value indicating whether policies from
                all projects will be returned.

        :returns: A generator of policy instances.
        """
        return self._list(_policy.Policy, paginated=True, **query)

    def update_policy(self, policy, **attrs):
        """Update a policy.

        :param policy: Either the name or the ID of a policy, or an instance
            of :class:`~openstack.cluster.v1.policy.Policy`.
        :param attrs: The attributes to update on the policy represented by
            the ``value`` parameter.

        :returns: The updated policy.
        :rtype: :class:`~openstack.cluster.v1.policy.Policy`
        """
        return self._update(_policy.Policy, policy, **attrs)

    def validate_policy(self, **attrs):
        """Validate a policy spec.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.policy.PolicyValidate`, it is
             comprised of the properties on the Policy class.

        :returns: The results of Policy validation.
        :rtype: :class:`~openstack.cluster.v1.policy.PolicyValidate`.
        """
        return self._create(_policy.PolicyValidate, **attrs)

    def cluster_policies(self, cluster, **query):
        """Retrieve a generator of cluster-policy bindings.

        :param cluster: The value can be the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.
        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the policies to be returned. Available parameters include:

            * enabled: A boolean value indicating whether the policy is
                       enabled on the cluster.
        :returns: A generator of cluster-policy binding instances.
        """
        cluster_id = resource2.Resource._get_id(cluster)
        return self._list(_cluster_policy.ClusterPolicy, paginated=False,
                          cluster_id=cluster_id, **query)

    def get_cluster_policy(self, cluster_policy, cluster):
        """Get a cluster-policy binding.

        :param cluster_policy:
            The value can be the name or ID of a policy or a
            :class:`~openstack.cluster.v1.policy.Policy` instance.
        :param cluster: The value can be the name or ID of a cluster or a
            :class:`~openstack.cluster.v1.cluster.Cluster` instance.

        :returns: a cluster-policy binding object.
        :rtype: :class:`~openstack.cluster.v1.cluster_policy.CLusterPolicy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            cluster-policy binding matching the criteria could be found.
        """
        return self._get(_cluster_policy.ClusterPolicy, cluster_policy,
                         cluster_id=cluster)

    def create_receiver(self, **attrs):
        """Create a new receiver from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
             :class:`~openstack.cluster.v1.receiver.Receiver`, it is comprised
             of the properties on the Receiver class.

        :returns: The results of receiver creation.
        :rtype: :class:`~openstack.cluster.v1.receiver.Receiver`.
        """
        return self._create(_receiver.Receiver, **attrs)

    def update_receiver(self, receiver, **attrs):
        """Update a receiver.

        :param receiver: The value can be either the name or ID of a receiver
            or a :class:`~openstack.cluster.v1.receiver.Receiver` instance.
        :param attrs: The attributes to update on the receiver parameter.
            Valid attribute names include ``name``, ``action`` and ``params``.
        :returns: The updated receiver.
        :rtype: :class:`~openstack.cluster.v1.receiver.Receiver`
        """
        return self._update(_receiver.Receiver, receiver, **attrs)

    def delete_receiver(self, receiver, ignore_missing=True):
        """Delete a receiver.

        :param receiver: The value can be either the name or ID of a receiver
            or a :class:`~openstack.cluster.v1.receiver.Receiver` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the receiver could not be found. When set to ``True``, no exception
            will be raised when attempting to delete a non-existent receiver.

        :returns: ``None``
        """
        self._delete(_receiver.Receiver, receiver,
                     ignore_missing=ignore_missing)

    def find_receiver(self, name_or_id, ignore_missing=True):
        """Find a single receiver.

        :param str name_or_id: The name or ID of a receiver.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the specified receiver does not exist. When
                    set to ``True``, None will be returned when attempting to
                    find a nonexistent receiver.
        :returns: A receiver object or None.
        :rtype: :class:`~openstack.cluster.v1.receiver.Receiver`
        """
        return self._find(_receiver.Receiver, name_or_id,
                          ignore_missing=ignore_missing)

    def get_receiver(self, receiver):
        """Get a single receiver.

        :param receiver: The value can be the name or ID of a receiver or a
            :class:`~openstack.cluster.v1.receiver.Receiver` instance.

        :returns: A receiver object.
        :rtype: :class:`~openstack.cluster.v1.receiver.Receiver`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            receiver matching the criteria could be found.
        """
        return self._get(_receiver.Receiver, receiver)

    def receivers(self, **query):
        """Retrieve a generator of receivers.

        :param kwargs \*\*query: Optional query parameters for restricting the
            receivers to be returned. Available parameters include:

            * name: The name of a receiver object.
            * type: The type of receiver objects.
            * cluster_id: The ID of the associated cluster.
            * action: The name of the associated action.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * global_project: A boolean value indicating whether receivers
            *   from all projects will be returned.

        :returns: A generator of receiver instances.
        """
        return self._list(_receiver.Receiver, paginated=True, **query)

    def get_action(self, action):
        """Get a single action.

        :param action: The value can be the name or ID of an action or a
            :class:`~openstack.cluster.v1.action.Action` instance.

        :returns: an action object.
        :rtype: :class:`~openstack.cluster.v1.action.Action`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            action matching the criteria could be found.
        """
        return self._get(_action.Action, action)

    def actions(self, **query):
        """Retrieve a generator of actions.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the actions to be returned. Available parameters include:

            * name: name of action for query.
            * target: ID of the target object for which the actions should be
                returned.
            * action: built-in action types for query.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of action instances.
        """
        return self._list(_action.Action, paginated=True, **query)

    def get_event(self, event):
        """Get a single event.

        :param event: The value can be the name or ID of an event or a
            :class:`~openstack.cluster.v1.event.Event` instance.

        :returns: an event object.
        :rtype: :class:`~openstack.cluster.v1.event.Event`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            event matching the criteria could be found.
        """
        return self._get(_event.Event, event)

    def events(self, **query):
        """Retrieve a generator of events.

        :param kwargs \*\*query: Optional query parameters to be sent to
            restrict the events to be returned. Available parameters include:

            * obj_name: name string of the object associated with an event.
            * obj_type: type string of the object related to an event. The
                        value can be ``cluster``, ``node``, ``policy`` etc.
            * obj_id: ID of the object associated with an event.
            * cluster_id: ID of the cluster associated with the event, if any.
            * action: name of the action associated with an event.
            * sort: A list of sorting keys separated by commas. Each sorting
                    key can optionally be attached with a sorting direction
                    modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
                query.  Returns a number of items up to the specified limit
                value.
            * marker: Specifies the ID of the last-seen item. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen item from the response as the marker parameter
                value in a subsequent limited request.
            * global_project: A boolean specifying whether events from all
                projects should be returned. This option is subject to access
                control checking.

        :returns: A generator of event instances.
        """
        return self._list(_event.Event, paginated=True, **query)

    def wait_for_status(self, resource, status, failures=[], interval=2,
                        wait=120):
        """Wait for a resource to be in a particular status.

        :param resource: The resource to wait on to reach the specified status.
                         The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource2.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        return resource2.wait_for_status(self._session, resource, status,
                                         failures, interval, wait)

    def wait_for_delete(self, resource, interval=2, wait=120):
        """Wait for a resource to be deleted.

        :param resource: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource2.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource2.wait_for_delete(self._session, resource, interval,
                                         wait)

    def services(self, **query):
        """Get a generator of service.

        :returns: A generator of objects that are of type
                  :class:`~openstack.cluster.v1.service.Service`
        """
        return self._list(_service.Service, paginated=False, **query)
