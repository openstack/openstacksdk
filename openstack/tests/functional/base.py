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
import sys
import time
import unittest

import os_client_config

from openstack.auth import service_filter
from openstack import connection
from openstack import exceptions
from openstack import profile
from openstack import utils


def requires_service(**kwargs):
    """Check whether a service is available for this test

    When the service exists, the test will be run as normal.
    When the service does not exist, the test will be skipped.

    Usage:
    @requires_service(service_type="identity", version="v3")
    def test_v3_auth(self):
        ...

    :param kwargs: The kwargs needed to create a
                   :class:`~openstack.auth.service_filter.ServiceFilter`.

    :returns: The test result if the test is executed.
    :raises: SkipTest, which is handled by the test runner.
    """
    def wrap(method):
        def check(self):
            try:
                self.conn.authenticator.get_endpoint(
                    self.conn.transport,
                    service_filter.ServiceFilter(**kwargs))
                return method(self)
            except exceptions.EndpointNotFound as exc:
                self.skip(exc.message)
        return check
    return wrap


class BaseFunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = os.getenv('OS_CLOUD', 'test_cloud')
        test_cloud = os_client_config.OpenStackConfig().get_one_cloud(name)

        prof = profile.Profile()
        prof.set_region(prof.ALL, test_cloud.region)
        if test_cloud.debug:
            utils.enable_logging(True, stream=sys.stdout)

        # TODO(thowe): There is a general smell here that this code is
        # repeated in two places at that we flatten the auth structure.
        # The connection class should take OCC config and just deal, but
        # I'd just like to get cacert working for now.
        auth = test_cloud.config['auth']
        if 'cacert' in test_cloud.config:
            auth['verify'] = test_cloud.config['cacert']
        if 'insecure' in test_cloud.config:
            auth['verify'] = not bool(test_cloud.config['insecure'])
        cls.conn = connection.Connection(profile=prof, **auth)

    @classmethod
    def assertIs(cls, expected, actual):
        if expected != actual:
            raise Exception(expected + ' != ' + actual)

    # TODO(thowe): This should probably be logic moved info the proxy or
    # or the resource, but for now I just want to get the functional tests
    # working again.
    @classmethod
    def wait_for_delete(cls, proxy_find, name_or_id, interval=2, linger=15,
                        wait=60):
        total_sleep = 0
        while total_sleep < wait:
            if proxy_find(name_or_id) is None:
                # Wait a little longer for the vestiges of the deleted object
                time.sleep(linger)
                return True
            print('waiting for delete ' + name_or_id)
            time.sleep(interval)
            total_sleep += interval
        return False
