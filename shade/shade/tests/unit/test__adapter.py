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

from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

from shade import _adapter
from shade.tests.unit import base


class TestExtractName(base.TestCase):

    scenarios = [
        ('slash_servers_bare', dict(url='/servers', parts=['servers'])),
        ('slash_servers_arg', dict(url='/servers/1', parts=['servers'])),
        ('servers_bare', dict(url='servers', parts=['servers'])),
        ('servers_arg', dict(url='servers/1', parts=['servers'])),
        ('networks_bare', dict(url='/v2.0/networks', parts=['networks'])),
        ('networks_arg', dict(url='/v2.0/networks/1', parts=['networks'])),
        ('tokens', dict(url='/v3/tokens', parts=['tokens'])),
        ('discovery', dict(url='/', parts=['discovery'])),
        ('secgroups', dict(
            url='/servers/1/os-security-groups',
            parts=['servers', 'os-security-groups'])),
    ]

    def test_extract_name(self):

        results = _adapter.extract_name(self.url)
        self.assertEqual(self.parts, results)
