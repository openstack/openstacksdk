# Copyright (c) 2016 Red Hat, Inc.
#
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

"""
test_devstack
-------------

Throw errors if we do not actually detect the services we're supposed to.
"""

import os

from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

from openstack.tests.functional import base


class TestDevstack(base.BaseFunctionalTest):
    scenarios = [
        ('designate', dict(env='DESIGNATE', service='dns')),
        ('heat', dict(env='HEAT', service='orchestration')),
        (
            'magnum',
            dict(env='MAGNUM', service='container-infrastructure-management'),
        ),
        ('neutron', dict(env='NEUTRON', service='network')),
        ('octavia', dict(env='OCTAVIA', service='load-balancer')),
        ('swift', dict(env='SWIFT', service='object-store')),
    ]

    def test_has_service(self):
        if os.environ.get(f'OPENSTACKSDK_HAS_{self.env}', '0') == '1':
            self.assertTrue(self.user_cloud.has_service(self.service))
