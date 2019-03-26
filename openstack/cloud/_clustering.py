# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import utils


class ClusteringCloudMixin(_normalize.Normalizer):

    @property
    def _clustering_client(self):
        if 'clustering' not in self._raw_clients:
            clustering_client = self._get_versioned_client(
                'clustering', min_version=1, max_version='1.latest')
            self._raw_clients['clustering'] = clustering_client
        return self._raw_clients['clustering']

    def create_cluster(self, name, profile, config=None, desired_capacity=0,
                       max_size=None, metadata=None, min_size=None,
                       timeout=None):
        profile = self.get_cluster_profile(profile)
        profile_id = profile['id']
        body = {
            'desired_capacity': desired_capacity,
            'name': name,
            'profile_id': profile_id
        }

        if config is not None:
            body['config'] = config

        if max_size is not None:
            body['max_size'] = max_size

        if metadata is not None:
            body['metadata'] = metadata

        if min_size is not None:
            body['min_size'] = min_size

        if timeout is not None:
            body['timeout'] = timeout

        data = self._clustering_client.post(
            '/clusters', json={'cluster': body},
            error_message="Error creating cluster {name}".format(name=name))

        return self._get_and_munchify(key=None, data=data)

    def set_cluster_metadata(self, name_or_id, metadata):
        cluster = self.get_cluster(name_or_id)
        if not cluster:
            raise exc.OpenStackCloudException(
                'Invalid Cluster {cluster}'.format(cluster=name_or_id))

        self._clustering_client.post(
            '/clusters/{cluster_id}/metadata'.format(cluster_id=cluster['id']),
            json={'metadata': metadata},
            error_message='Error updating cluster metadata')

    def get_cluster_by_id(self, cluster_id):
        try:
            data = self._clustering_client.get(
                "/clusters/{cluster_id}".format(cluster_id=cluster_id),
                error_message="Error fetching cluster {name}".format(
                    name=cluster_id))
            return self._get_and_munchify('cluster', data)
        except Exception:
            return None

    def get_cluster(self, name_or_id, filters=None):
        return _utils._get_entity(
            cloud=self, resource='cluster',
            name_or_id=name_or_id, filters=filters)

    def update_cluster(self, name_or_id, new_name=None,
                       profile_name_or_id=None, config=None, metadata=None,
                       timeout=None, profile_only=False):
        old_cluster = self.get_cluster(name_or_id)
        if old_cluster is None:
            raise exc.OpenStackCloudException(
                'Invalid Cluster {cluster}'.format(cluster=name_or_id))
        cluster = {
            'profile_only': profile_only
        }

        if config is not None:
            cluster['config'] = config

        if metadata is not None:
            cluster['metadata'] = metadata

        if profile_name_or_id is not None:
            profile = self.get_cluster_profile(profile_name_or_id)
            if profile is None:
                raise exc.OpenStackCloudException(
                    'Invalid Cluster Profile {profile}'.format(
                        profile=profile_name_or_id))
            cluster['profile_id'] = profile.id

        if timeout is not None:
            cluster['timeout'] = timeout

        if new_name is not None:
            cluster['name'] = new_name

        data = self._clustering_client.patch(
            "/clusters/{cluster_id}".format(cluster_id=old_cluster['id']),
            json={'cluster': cluster},
            error_message="Error updating cluster "
                          "{name}".format(name=name_or_id))

        return self._get_and_munchify(key=None, data=data)

    def delete_cluster(self, name_or_id):
        cluster = self.get_cluster(name_or_id)
        if cluster is None:
            self.log.debug("Cluster %s not found for deleting", name_or_id)
            return False

        for policy in self.list_policies_on_cluster(name_or_id):
            detach_policy = self.get_cluster_policy_by_id(
                policy['policy_id'])
            self.detach_policy_from_cluster(cluster, detach_policy)

        for receiver in self.list_cluster_receivers():
            if cluster["id"] == receiver["cluster_id"]:
                self.delete_cluster_receiver(receiver["id"], wait=True)

        self._clustering_client.delete(
            "/clusters/{cluster_id}".format(cluster_id=name_or_id),
            error_message="Error deleting cluster {name}".format(
                name=name_or_id))

        return True

    def search_clusters(self, name_or_id=None, filters=None):
        clusters = self.list_clusters()
        return _utils._filter_list(clusters, name_or_id, filters)

    def list_clusters(self):
        try:
            data = self._clustering_client.get(
                '/clusters',
                error_message="Error fetching clusters")
            return self._get_and_munchify('clusters', data)
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return []

    def attach_policy_to_cluster(self, name_or_id, policy_name_or_id,
                                 is_enabled):
        cluster = self.get_cluster(name_or_id)
        policy = self.get_cluster_policy(policy_name_or_id)
        if cluster is None:
            raise exc.OpenStackCloudException(
                'Cluster {cluster} not found for attaching'.format(
                    cluster=name_or_id))

        if policy is None:
            raise exc.OpenStackCloudException(
                'Policy {policy} not found for attaching'.format(
                    policy=policy_name_or_id))

        body = {
            'policy_id': policy['id'],
            'enabled': is_enabled
        }

        self._clustering_client.post(
            "/clusters/{cluster_id}/actions".format(cluster_id=cluster['id']),
            error_message="Error attaching policy {policy} to cluster "
                          "{cluster}".format(
                policy=policy['id'],
                cluster=cluster['id']),
            json={'policy_attach': body})

        return True

    def detach_policy_from_cluster(
            self, name_or_id, policy_name_or_id, wait=False, timeout=3600):
        cluster = self.get_cluster(name_or_id)
        policy = self.get_cluster_policy(policy_name_or_id)
        if cluster is None:
            raise exc.OpenStackCloudException(
                'Cluster {cluster} not found for detaching'.format(
                    cluster=name_or_id))

        if policy is None:
            raise exc.OpenStackCloudException(
                'Policy {policy} not found for detaching'.format(
                    policy=policy_name_or_id))

        body = {'policy_id': policy['id']}
        self._clustering_client.post(
            "/clusters/{cluster_id}/actions".format(cluster_id=cluster['id']),
            error_message="Error detaching policy {policy} from cluster "
                          "{cluster}".format(
                policy=policy['id'],
                cluster=cluster['id']),
            json={'policy_detach': body})

        if not wait:
            return True

        value = []

        for count in utils.iterate_timeout(
                timeout, "Timeout waiting for cluster policy to detach"):

            # TODO(bjjohnson) This logic will wait until there are no policies.
            # Since we're detaching a specific policy, checking to make sure
            # that policy is not in the list of policies would be better.
            policy_status = self.get_cluster_by_id(cluster['id'])['policies']

            if policy_status == value:
                break
        return True

    def update_policy_on_cluster(self, name_or_id, policy_name_or_id,
                                 is_enabled):
        cluster = self.get_cluster(name_or_id)
        policy = self.get_cluster_policy(policy_name_or_id)
        if cluster is None:
            raise exc.OpenStackCloudException(
                'Cluster {cluster} not found for updating'.format(
                    cluster=name_or_id))

        if policy is None:
            raise exc.OpenStackCloudException(
                'Policy {policy} not found for updating'.format(
                    policy=policy_name_or_id))

        body = {
            'policy_id': policy['id'],
            'enabled': is_enabled
        }
        self._clustering_client.post(
            "/clusters/{cluster_id}/actions".format(cluster_id=cluster['id']),
            error_message="Error updating policy {policy} on cluster "
                          "{cluster}".format(
                policy=policy['id'],
                cluster=cluster['id']),
            json={'policy_update': body})

        return True

    def get_policy_on_cluster(self, name_or_id, policy_name_or_id):
        try:
            policy = self._clustering_client.get(
                "/clusters/{cluster_id}/policies/{policy_id}".format(
                    cluster_id=name_or_id, policy_id=policy_name_or_id),
                error_message="Error fetching policy "
                              "{name}".format(name=policy_name_or_id))
            return self._get_and_munchify('cluster_policy', policy)
        except Exception:
            return False

    def list_policies_on_cluster(self, name_or_id):
        endpoint = "/clusters/{cluster_id}/policies".format(
            cluster_id=name_or_id)
        try:
            data = self._clustering_client.get(
                endpoint,
                error_message="Error fetching cluster policies")
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return []
        return self._get_and_munchify('cluster_policies', data)

    def create_cluster_profile(self, name, spec, metadata=None):
        profile = {
            'name': name,
            'spec': spec
        }

        if metadata is not None:
            profile['metadata'] = metadata

        data = self._clustering_client.post(
            '/profiles', json={'profile': profile},
            error_message="Error creating profile {name}".format(name=name))

        return self._get_and_munchify('profile', data)

    def set_cluster_profile_metadata(self, name_or_id, metadata):
        profile = self.get_cluster_profile(name_or_id)
        if not profile:
            raise exc.OpenStackCloudException(
                'Invalid Profile {profile}'.format(profile=name_or_id))

        self._clustering_client.post(
            '/profiles/{profile_id}/metadata'.format(profile_id=profile['id']),
            json={'metadata': metadata},
            error_message='Error updating profile metadata')

    def search_cluster_profiles(self, name_or_id=None, filters=None):
        cluster_profiles = self.list_cluster_profiles()
        return _utils._filter_list(cluster_profiles, name_or_id, filters)

    def list_cluster_profiles(self):
        try:
            data = self._clustering_client.get(
                '/profiles',
                error_message="Error fetching profiles")
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return []
        return self._get_and_munchify('profiles', data)

    def get_cluster_profile_by_id(self, profile_id):
        try:
            data = self._clustering_client.get(
                "/profiles/{profile_id}".format(profile_id=profile_id),
                error_message="Error fetching profile {name}".format(
                    name=profile_id))
            return self._get_and_munchify('profile', data)
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return None

    def get_cluster_profile(self, name_or_id, filters=None):
        return _utils._get_entity(self, 'cluster_profile', name_or_id, filters)

    def delete_cluster_profile(self, name_or_id):
        profile = self.get_cluster_profile(name_or_id)
        if profile is None:
            self.log.debug("Profile %s not found for deleting", name_or_id)
            return False

        for cluster in self.list_clusters():
            if (name_or_id, profile.id) in cluster.items():
                self.log.debug(
                    "Profile %s is being used by cluster %s, won't delete",
                    name_or_id, cluster.name)
                return False

        self._clustering_client.delete(
            "/profiles/{profile_id}".format(profile_id=profile['id']),
            error_message="Error deleting profile "
                          "{name}".format(name=name_or_id))

        return True

    def update_cluster_profile(self, name_or_id, metadata=None, new_name=None):
        old_profile = self.get_cluster_profile(name_or_id)
        if not old_profile:
            raise exc.OpenStackCloudException(
                'Invalid Profile {profile}'.format(profile=name_or_id))

        profile = {}

        if metadata is not None:
            profile['metadata'] = metadata

        if new_name is not None:
            profile['name'] = new_name

        data = self._clustering_client.patch(
            "/profiles/{profile_id}".format(profile_id=old_profile.id),
            json={'profile': profile},
            error_message="Error updating profile {name}".format(
                name=name_or_id))

        return self._get_and_munchify(key=None, data=data)

    def create_cluster_policy(self, name, spec):
        policy = {
            'name': name,
            'spec': spec
        }

        data = self._clustering_client.post(
            '/policies', json={'policy': policy},
            error_message="Error creating policy {name}".format(
                name=policy['name']))
        return self._get_and_munchify('policy', data)

    def search_cluster_policies(self, name_or_id=None, filters=None):
        cluster_policies = self.list_cluster_policies()
        return _utils._filter_list(cluster_policies, name_or_id, filters)

    def list_cluster_policies(self):
        endpoint = "/policies"
        try:
            data = self._clustering_client.get(
                endpoint,
                error_message="Error fetching cluster policies")
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return []
        return self._get_and_munchify('policies', data)

    def get_cluster_policy_by_id(self, policy_id):
        try:
            data = self._clustering_client.get(
                "/policies/{policy_id}".format(policy_id=policy_id),
                error_message="Error fetching policy {name}".format(
                    name=policy_id))
            return self._get_and_munchify('policy', data)
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return None

    def get_cluster_policy(self, name_or_id, filters=None):
        return _utils._get_entity(
            self, 'cluster_policie', name_or_id, filters)

    def delete_cluster_policy(self, name_or_id):
        policy = self.get_cluster_policy_by_id(name_or_id)
        if policy is None:
            self.log.debug("Policy %s not found for deleting", name_or_id)
            return False

        for cluster in self.list_clusters():
            if (name_or_id, policy.id) in cluster.items():
                self.log.debug(
                    "Policy %s is being used by cluster %s, won't delete",
                    name_or_id, cluster.name)
                return False

        self._clustering_client.delete(
            "/policies/{policy_id}".format(policy_id=name_or_id),
            error_message="Error deleting policy "
                          "{name}".format(name=name_or_id))

        return True

    def update_cluster_policy(self, name_or_id, new_name):
        old_policy = self.get_cluster_policy(name_or_id)
        if not old_policy:
            raise exc.OpenStackCloudException(
                'Invalid Policy {policy}'.format(policy=name_or_id))
        policy = {'name': new_name}

        data = self._clustering_client.patch(
            "/policies/{policy_id}".format(policy_id=old_policy.id),
            json={'policy': policy},
            error_message="Error updating policy "
                          "{name}".format(name=name_or_id))
        return self._get_and_munchify(key=None, data=data)

    def create_cluster_receiver(self, name, receiver_type,
                                cluster_name_or_id=None, action=None,
                                actor=None, params=None):
        cluster = self.get_cluster(cluster_name_or_id)
        if cluster is None:
            raise exc.OpenStackCloudException(
                'Invalid cluster {cluster}'.format(cluster=cluster_name_or_id))

        receiver = {
            'name': name,
            'type': receiver_type
        }

        if cluster_name_or_id is not None:
            receiver['cluster_id'] = cluster.id

        if action is not None:
            receiver['action'] = action

        if actor is not None:
            receiver['actor'] = actor

        if params is not None:
            receiver['params'] = params

        data = self._clustering_client.post(
            '/receivers', json={'receiver': receiver},
            error_message="Error creating receiver {name}".format(name=name))
        return self._get_and_munchify('receiver', data)

    def search_cluster_receivers(self, name_or_id=None, filters=None):
        cluster_receivers = self.list_cluster_receivers()
        return _utils._filter_list(cluster_receivers, name_or_id, filters)

    def list_cluster_receivers(self):
        try:
            data = self._clustering_client.get(
                '/receivers',
                error_message="Error fetching receivers")
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return []
        return self._get_and_munchify('receivers', data)

    def get_cluster_receiver_by_id(self, receiver_id):
        try:
            data = self._clustering_client.get(
                "/receivers/{receiver_id}".format(receiver_id=receiver_id),
                error_message="Error fetching receiver {name}".format(
                    name=receiver_id))
            return self._get_and_munchify('receiver', data)
        except exc.OpenStackCloudURINotFound as e:
            self.log.debug(str(e), exc_info=True)
            return None

    def get_cluster_receiver(self, name_or_id, filters=None):
        return _utils._get_entity(
            self, 'cluster_receiver', name_or_id, filters)

    def delete_cluster_receiver(self, name_or_id, wait=False, timeout=3600):
        receiver = self.get_cluster_receiver(name_or_id)
        if receiver is None:
            self.log.debug("Receiver %s not found for deleting", name_or_id)
            return False

        receiver_id = receiver['id']

        self._clustering_client.delete(
            "/receivers/{receiver_id}".format(receiver_id=receiver_id),
            error_message="Error deleting receiver {name}".format(
                name=name_or_id))

        if not wait:
            return True

        for count in utils.iterate_timeout(
                timeout, "Timeout waiting for cluster receiver to delete"):

            receiver = self.get_cluster_receiver_by_id(receiver_id)

            if not receiver:
                break

        return True

    def update_cluster_receiver(self, name_or_id, new_name=None, action=None,
                                params=None):
        old_receiver = self.get_cluster_receiver(name_or_id)
        if old_receiver is None:
            raise exc.OpenStackCloudException(
                'Invalid receiver {receiver}'.format(receiver=name_or_id))

        receiver = {}

        if new_name is not None:
            receiver['name'] = new_name

        if action is not None:
            receiver['action'] = action

        if params is not None:
            receiver['params'] = params

        data = self._clustering_client.patch(
            "/receivers/{receiver_id}".format(receiver_id=old_receiver.id),
            json={'receiver': receiver},
            error_message="Error updating receiver {name}".format(
                name=name_or_id))
        return self._get_and_munchify(key=None, data=data)
