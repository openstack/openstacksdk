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

"""
test_clustering
----------------------------------

Functional tests for `shade` clustering methods.
"""

from testtools import content

from openstack.tests.functional import base

import time


def wait_for_status(client, client_args, field, value, check_interval=1,
                    timeout=60):
    """Wait for an OpenStack resource to enter a specified state

    :param client: An uncalled client resource to be called with resource_args
    :param client_args: Arguments to be passed to client
    :param field: Dictionary field to check
    :param value: Dictionary value to look for
    :param check_interval: Interval between checks
    :param timeout: Time in seconds to wait for status to update.
    :returns: True if correct status was reached
    :raises: TimeoutException
    """
    resource_status = client(**client_args)[field]
    start = time.time()

    while resource_status != value:
        time.sleep(check_interval)
        resource = client(**client_args)
        resource_status = resource[field]

        timed_out = time.time() - start >= timeout

        if resource_status != value and timed_out:
            return False
    return True


def wait_for_create(client, client_args, check_interval=1, timeout=60):
    """Wait for an OpenStack resource to be created

     :param client: An uncalled client resource to be called with resource_args
     :param client_args: Arguments to be passed to client
     :param name: Name of the resource (for logging)
     :param check_interval: Interval between checks
     :param timeout: Time in seconds to wait for status to update.
     :returns: True if openstack.exceptions.NotFoundException is caught
     :raises: TimeoutException

     """

    resource = client(**client_args)
    start = time.time()

    while not resource:
        time.sleep(check_interval)
        resource = client(**client_args)

        timed_out = time.time() - start >= timeout

        if (not resource) and timed_out:
            return False
    return True


def wait_for_delete(client, client_args, check_interval=1, timeout=60):
    """Wait for an OpenStack resource to 404/delete

    :param client: An uncalled client resource to be called with resource_args
    :param client_args: Arguments to be passed to client
    :param name: Name of the resource (for logging)
    :param check_interval: Interval between checks
    :param timeout: Time in seconds to wait for status to update.
    :returns: True if openstack.exceptions.NotFoundException is caught
    :raises: TimeoutException

    """
    resource = client(**client_args)
    start = time.time()

    while resource:
        time.sleep(check_interval)
        resource = client(**client_args)

        timed_out = time.time() - start >= timeout

        if resource and timed_out:
            return False
    return True


class TestClustering(base.BaseFunctionalTest):

    def setUp(self):
        super(TestClustering, self).setUp()
        self.skipTest('clustering service not supported by cloud')

    def test_create_profile(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        self.assertEqual(profile['name'], profile_name)
        self.assertEqual(profile['spec'], spec)

    def test_create_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        self.assertEqual(cluster['cluster']['name'], cluster_name)
        self.assertEqual(cluster['cluster']['profile_id'], profile['id'])
        self.assertEqual(cluster['cluster']['desired_capacity'],
                         desired_capacity)

    def test_get_cluster_by_id(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])
        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        # Test that we get the same cluster with the get_cluster method
        cluster_get = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        self.assertEqual(cluster_get['id'], cluster['cluster']['id'])

    def test_update_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        # Test that we can update a field on the cluster and only that field
        # is updated

        self.user_cloud.update_cluster(cluster['cluster']['id'],
                                       new_name='new_cluster_name')

        wait = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'status', 'ACTIVE')

        self.assertTrue(wait)
        cluster_update = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        self.assertEqual(cluster_update['id'], cluster['cluster']['id'])
        self.assertEqual(cluster_update['name'], 'new_cluster_name')
        self.assertEqual(cluster_update['profile_id'],
                         cluster['cluster']['profile_id'])
        self.assertEqual(cluster_update['desired_capacity'],
                         cluster['cluster']['desired_capacity'])

    def test_create_cluster_policy(self):
        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        self.assertEqual(policy['name'], policy_name)
        self.assertEqual(policy['spec'], spec)

    def test_attach_policy_to_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'],
                        cluster['cluster']['id'])

        # Test that we can attach policy to cluster and get True returned

        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        policy_attach = self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)
        self.assertTrue(policy_attach)

    def test_detach_policy_from_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'],
                        cluster['cluster']['id'])

        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)

        wait = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'policies',
            ['{policy}'.format(policy=policy['id'])])

        policy_detach = self.user_cloud.detach_policy_from_cluster(
            attach_cluster, attach_policy)

        self.assertTrue(policy_detach)
        self.assertTrue(wait)

    def test_get_policy_on_cluster_by_id(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'],
                        cluster['cluster']['id'])

        # Test that we can attach policy to cluster and get True returned

        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        policy_attach = self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)
        self.assertTrue(policy_attach)

        wait = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'policies',
            ["{policy}".format(policy=policy['id'])])

        # Test that we get the same policy with the get_policy_on_cluster
        # method

        cluster_policy_get = self.user_cloud.get_policy_on_cluster(
            cluster['cluster']["id"], policy['id'])

        self.assertEqual(cluster_policy_get['cluster_id'],
                         cluster['cluster']["id"])
        self.assertEqual(cluster_policy_get['cluster_name'],
                         cluster['cluster']["name"])
        self.assertEqual(cluster_policy_get['policy_id'], policy['id']),
        self.assertEqual(cluster_policy_get['policy_name'], policy['name'])
        self.assertTrue(wait)

    def test_list_policies_on_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'],
                        cluster['cluster']['id'])

        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)

        wait = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'policies',
            ["{policy}".format(policy=policy['id'])])

        cluster_policy = self.user_cloud.get_policy_on_cluster(
            name_or_id=cluster['cluster']['id'],
            policy_name_or_id=policy['id'])

        policy_list = {"cluster_policies": [cluster_policy]}

        # Test that we can list the policies on a cluster
        cluster_policies = self.user_cloud.list_policies_on_cluster(
            cluster['cluster']["id"])
        self.assertEqual(
            cluster_policies, policy_list)
        self.assertTrue(wait)

    def test_create_cluster_receiver(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        receiver_name = "example_receiver"
        receiver_type = "webhook"

        self.addDetail('receiver', content.text_content(receiver_name))

        # Test that we can create a receiver and we get it returned

        receiver = self.user_cloud.create_cluster_receiver(
            name=receiver_name, receiver_type=receiver_type,
            cluster_name_or_id=cluster['cluster']['id'],
            action='CLUSTER_SCALE_OUT')

        self.addCleanup(self.cleanup_receiver, receiver['id'])

        self.assertEqual(receiver['name'], receiver_name)
        self.assertEqual(receiver['type'], receiver_type)
        self.assertEqual(receiver['cluster_id'], cluster['cluster']["id"])

    def test_list_cluster_receivers(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        receiver_name = "example_receiver"
        receiver_type = "webhook"

        self.addDetail('receiver', content.text_content(receiver_name))

        # Test that we can create a receiver and we get it returned

        receiver = self.user_cloud.create_cluster_receiver(
            name=receiver_name, receiver_type=receiver_type,
            cluster_name_or_id=cluster['cluster']['id'],
            action='CLUSTER_SCALE_OUT')

        self.addCleanup(self.cleanup_receiver, receiver['id'])

        get_receiver = self.user_cloud.get_cluster_receiver_by_id(
            receiver['id'])
        receiver_list = {"receivers": [get_receiver]}

        # Test that we can list receivers

        receivers = self.user_cloud.list_cluster_receivers()
        self.assertEqual(receivers, receiver_list)

    def test_delete_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        # Test that we can attach policy to cluster and get True returned
        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)

        receiver_name = "example_receiver"
        receiver_type = "webhook"

        self.addDetail('receiver', content.text_content(receiver_name))

        # Test that we can create a receiver and we get it returned

        self.user_cloud.create_cluster_receiver(
            name=receiver_name, receiver_type=receiver_type,
            cluster_name_or_id=cluster['cluster']['id'],
            action='CLUSTER_SCALE_OUT')

        # Test that we can delete cluster and get True returned
        cluster_delete = self.user_cloud.delete_cluster(
            cluster['cluster']['id'])
        self.assertTrue(cluster_delete)

    def test_list_clusters(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        wait = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'status', 'ACTIVE')

        get_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])

        # Test that we can list clusters
        clusters = self.user_cloud.list_clusters()
        self.assertEqual(clusters, [get_cluster])
        self.assertTrue(wait)

    def test_update_policy_on_cluster(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'],
                        cluster['cluster']['id'])

        # Test that we can attach policy to cluster and get True returned

        attach_cluster = self.user_cloud.get_cluster_by_id(
            cluster['cluster']['id'])
        attach_policy = self.user_cloud.get_cluster_policy_by_id(
            policy['id'])

        self.user_cloud.attach_policy_to_cluster(
            attach_cluster, attach_policy, is_enabled=True)

        wait_attach = wait_for_status(
            self.user_cloud.get_cluster_by_id,
            {'name_or_id': cluster['cluster']['id']}, 'policies',
            ["{policy}".format(policy=policy['id'])])

        get_old_policy = self.user_cloud.get_policy_on_cluster(
            cluster['cluster']["id"], policy['id'])

        # Test that we can update the policy on cluster
        policy_update = self.user_cloud.update_policy_on_cluster(
            attach_cluster, attach_policy, is_enabled=False)

        get_old_policy.update({'enabled': False})

        wait_update = wait_for_status(
            self.user_cloud.get_policy_on_cluster,
            {'name_or_id': cluster['cluster']['id'],
             'policy_name_or_id': policy['id']}, 'enabled',
            False)

        get_new_policy = self.user_cloud.get_policy_on_cluster(
            cluster['cluster']["id"], policy['id'])

        get_old_policy['last_op'] = None
        get_new_policy['last_op'] = None

        self.assertTrue(policy_update)
        self.assertEqual(get_new_policy, get_old_policy)
        self.assertTrue(wait_attach)
        self.assertTrue(wait_update)

    def test_list_cluster_profiles(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        # Test that we can list profiles

        wait = wait_for_create(self.user_cloud.get_cluster_profile_by_id,
                               {'name_or_id': profile['id']})

        get_profile = self.user_cloud.get_cluster_profile_by_id(profile['id'])

        profiles = self.user_cloud.list_cluster_profiles()
        self.assertEqual(profiles, [get_profile])
        self.assertTrue(wait)

    def test_get_cluster_profile_by_id(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        profile_get = self.user_cloud.get_cluster_profile_by_id(profile['id'])

        # Test that we get the same profile with the get_profile method
        # Format of the created_at variable differs between policy create
        # and policy get so if we don't ignore this variable, comparison will
        # always fail
        profile['created_at'] = 'ignore'
        profile_get['created_at'] = 'ignore'

        self.assertEqual(profile_get, profile)

    def test_update_cluster_profile(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        # Test that we can update a field on the profile and only that field
        # is updated

        profile_update = self.user_cloud.update_cluster_profile(
            profile['id'], new_name='new_profile_name')
        self.assertEqual(profile_update['profile']['id'], profile['id'])
        self.assertEqual(profile_update['profile']['spec'], profile['spec'])
        self.assertEqual(profile_update['profile']['name'], 'new_profile_name')

    def test_delete_cluster_profile(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        # Test that we can delete a profile and get True returned
        profile_delete = self.user_cloud.delete_cluster_profile(profile['id'])
        self.assertTrue(profile_delete)

    def test_list_cluster_policies(self):
        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        policy_get = self.user_cloud.get_cluster_policy_by_id(policy['id'])

        # Test that we can list policies

        policies = self.user_cloud.list_cluster_policies()

        # Format of the created_at variable differs between policy create
        # and policy get so if we don't ignore this variable, comparison will
        # always fail
        policies[0]['created_at'] = 'ignore'
        policy_get['created_at'] = 'ignore'

        self.assertEqual(policies, [policy_get])

    def test_get_cluster_policy_by_id(self):
        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        # Test that we get the same policy with the get_policy method

        policy_get = self.user_cloud.get_cluster_policy_by_id(policy['id'])

        # Format of the created_at variable differs between policy create
        # and policy get so if we don't ignore this variable, comparison will
        # always fail
        policy['created_at'] = 'ignore'
        policy_get['created_at'] = 'ignore'

        self.assertEqual(policy_get, policy)

    def test_update_cluster_policy(self):
        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        # Test that we can update a field on the policy and only that field
        # is updated

        policy_update = self.user_cloud.update_cluster_policy(
            policy['id'], new_name='new_policy_name')
        self.assertEqual(policy_update['policy']['id'], policy['id'])
        self.assertEqual(policy_update['policy']['spec'], policy['spec'])
        self.assertEqual(policy_update['policy']['name'], 'new_policy_name')

    def test_delete_cluster_policy(self):
        policy_name = 'example_policy'
        spec = {
            "properties": {
                "adjustment": {
                    "min_step": 1,
                    "number": 1,
                    "type": "CHANGE_IN_CAPACITY"
                },
                "event": "CLUSTER_SCALE_IN"
            },
            "type": "senlin.policy.scaling",
            "version": "1.0"
        }

        self.addDetail('policy', content.text_content(policy_name))

        # Test that we can create a policy and we get it returned

        policy = self.user_cloud.create_cluster_policy(name=policy_name,
                                                       spec=spec)

        self.addCleanup(self.cleanup_policy, policy['id'])

        # Test that we can delete a policy and get True returned
        policy_delete = self.user_cloud.delete_cluster_policy(
            policy['id'])
        self.assertTrue(policy_delete)

    def test_get_cluster_receiver_by_id(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        receiver_name = "example_receiver"
        receiver_type = "webhook"

        self.addDetail('receiver', content.text_content(receiver_name))

        # Test that we can create a receiver and we get it returned

        receiver = self.user_cloud.create_cluster_receiver(
            name=receiver_name, receiver_type=receiver_type,
            cluster_name_or_id=cluster['cluster']['id'],
            action='CLUSTER_SCALE_OUT')

        self.addCleanup(self.cleanup_receiver, receiver['id'])

        # Test that we get the same receiver with the get_receiver method

        receiver_get = self.user_cloud.get_cluster_receiver_by_id(
            receiver['id'])
        self.assertEqual(receiver_get['id'], receiver["id"])

    def test_update_cluster_receiver(self):
        profile_name = "test_profile"
        spec = {
            "properties": {
                "flavor": "m1.tiny",
                "image": base.IMAGE_NAME,
                "networks": [
                    {
                        "network": "private"
                    }
                ],
                "security_groups": [
                    "default"
                ]
            },
            "type": "os.nova.server",
            "version": 1.0
        }

        self.addDetail('profile', content.text_content(profile_name))
        # Test that we can create a profile and we get it returned

        profile = self.user_cloud.create_cluster_profile(name=profile_name,
                                                         spec=spec)

        self.addCleanup(self.cleanup_profile, profile['id'])

        cluster_name = 'example_cluster'
        desired_capacity = 0

        self.addDetail('cluster', content.text_content(cluster_name))

        # Test that we can create a cluster and we get it returned
        cluster = self.user_cloud.create_cluster(
            name=cluster_name, profile=profile,
            desired_capacity=desired_capacity)

        self.addCleanup(self.cleanup_cluster, cluster['cluster']['id'])

        receiver_name = "example_receiver"
        receiver_type = "webhook"

        self.addDetail('receiver', content.text_content(receiver_name))

        # Test that we can create a receiver and we get it returned

        receiver = self.user_cloud.create_cluster_receiver(
            name=receiver_name, receiver_type=receiver_type,
            cluster_name_or_id=cluster['cluster']['id'],
            action='CLUSTER_SCALE_OUT')

        self.addCleanup(self.cleanup_receiver, receiver['id'])

        # Test that we can update a field on the receiver and only that field
        # is updated

        receiver_update = self.user_cloud.update_cluster_receiver(
            receiver['id'], new_name='new_receiver_name')
        self.assertEqual(receiver_update['receiver']['id'], receiver['id'])
        self.assertEqual(receiver_update['receiver']['type'], receiver['type'])
        self.assertEqual(receiver_update['receiver']['cluster_id'],
                         receiver['cluster_id'])
        self.assertEqual(receiver_update['receiver']['name'],
                         'new_receiver_name')

    def cleanup_profile(self, name):
        time.sleep(5)
        for cluster in self.user_cloud.list_clusters():
            if name == cluster["profile_id"]:
                self.user_cloud.delete_cluster(cluster["id"])
        self.user_cloud.delete_cluster_profile(name)

    def cleanup_cluster(self, name):
        self.user_cloud.delete_cluster(name)

    def cleanup_policy(self, name, cluster_name=None):
        if cluster_name is not None:
            cluster = self.user_cloud.get_cluster_by_id(cluster_name)
            policy = self.user_cloud.get_cluster_policy_by_id(name)
            policy_status = \
                self.user_cloud.get_cluster_by_id(cluster['id'])['policies']
            if policy_status != []:
                self.user_cloud.detach_policy_from_cluster(cluster, policy)
        self.user_cloud.delete_cluster_policy(name)

    def cleanup_receiver(self, name):
        self.user_cloud.delete_cluster_receiver(name)
