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

import uuid

from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import domain_config as _domain_config
from openstack.tests.functional import base


class TestDomainConfig(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.domain_name = self.getUniqueString()

        # create the domain and domain config

        self.domain = self.operator_cloud.create_domain(
            name=self.domain_name,
        )
        self.assertIsInstance(self.domain, _domain.Domain)
        self.addCleanup(self._delete_domain)

    def _delete_domain(self):
        self.operator_cloud.identity.update_domain(
            self.domain,
            enabled=False,
        )
        self.operator_cloud.identity.delete_domain(self.domain)

    def test_domain_config(self):
        # create the domain config

        domain_config = self.operator_cloud.identity.create_domain_config(
            self.domain,
            identity={'driver': uuid.uuid4().hex},
            ldap={'url': uuid.uuid4().hex},
        )
        self.assertIsInstance(
            domain_config,
            _domain_config.DomainConfig,
        )

        # update the domain config

        ldap_url = uuid.uuid4().hex
        domain_config = self.operator_cloud.identity.update_domain_config(
            self.domain,
            ldap={'url': ldap_url},
        )
        self.assertIsInstance(
            domain_config,
            _domain_config.DomainConfig,
        )

        # retrieve details of the (updated) domain config

        domain_config = self.operator_cloud.identity.get_domain_config(
            self.domain,
        )
        self.assertIsInstance(
            domain_config,
            _domain_config.DomainConfig,
        )
        self.assertEqual(ldap_url, domain_config.ldap.url)

        # delete the domain config

        result = self.operator_cloud.identity.delete_domain_config(
            self.domain,
            ignore_missing=False,
        )
        self.assertIsNone(result)
