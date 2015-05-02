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

import unittest

import os_client_config

from openstack import connection
from openstack import user_preference


class BaseFunctionalTest(unittest.TestCase):
    def setUp(self):
        test_cloud = os_client_config.OpenStackConfig().get_one_cloud(
            'test_cloud')

        pref = user_preference.UserPreference()
        pref.set_region(pref.ALL, test_cloud.region)

        self.conn = connection.Connection(
            preference=pref,
            **test_cloud.config['auth'])
