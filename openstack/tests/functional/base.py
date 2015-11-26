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

from openstack import connection


CLOUD_NAME = os.getenv('OS_CLOUD', 'test_cloud')


def requires_service(**kwargs):
    """Check whether a service is available for this test

    When the service exists, the test will be run as normal.
    When the service does not exist, the test will be skipped.

    Usage:
    @requires_service(service_type="identity", version="v3")
    def test_v3_auth(self):
        ...

    :param kwargs: The kwargs needed to filter an endpoint.
    :returns: The test result if the test is executed.
    :raises: SkipTest, which is handled by the test runner.
    """
    def wrap(method):
        def check(self):
            ep = self.conn.session.get_endpoint(**kwargs)
            if ep is None:
                self.skip('Service endpoint not found.')
            return method(self)
        return check
    return wrap


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
