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

import os
import time
import unittest

from keystoneauth1 import exceptions as _exceptions
from openstack import connection


CLOUD_NAME = os.getenv('OS_CLOUD', 'test_cloud')


def service_exists(**kwargs):
    """Decorator function to check whether a service exists

    Usage:
    @unittest.skipUnless(base.service_exists(service_type="metering"),
                         "Metering service does not exist")
    class TestMeter(base.BaseFunctionalTest):
        ...

    :param kwargs: The kwargs needed to filter an endpoint.
    :returns: True if the service exists, otherwise False.
    """
    try:
        conn = connection.from_config(cloud_name=CLOUD_NAME)
        conn.session.get_endpoint(**kwargs)

        return True
    except _exceptions.EndpointNotFound:
        return False


class BaseFunctionalTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = connection.from_config(cloud_name=CLOUD_NAME)

    @classmethod
    def assertIs(cls, expected, actual):
        if expected != actual:
            raise Exception(expected + ' != ' + actual)

    @classmethod
    def linger_for_delete(cls):
        time.sleep(40)
