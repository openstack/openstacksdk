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
test_stack
----------------------------------

Functional tests for `shade` stack methods.
"""

import tempfile

from openstack.cloud import exc
from openstack.tests import fakes
from openstack.tests.functional.cloud import base

simple_template = '''heat_template_version: 2014-10-16
parameters:
  length:
    type: number
    default: 10

resources:
  my_rand:
    type: OS::Heat::RandomString
    properties:
      length: {get_param: length}
outputs:
  rand:
    value:
      get_attr: [my_rand, value]
'''

root_template = '''heat_template_version: 2014-10-16
parameters:
  length:
    type: number
    default: 10
  count:
    type: number
    default: 5

resources:
  my_rands:
    type: OS::Heat::ResourceGroup
    properties:
      count: {get_param: count}
      resource_def:
        type: My::Simple::Template
        properties:
          length: {get_param: length}
outputs:
  rands:
    value:
      get_attr: [my_rands, attributes, rand]
'''

environment = '''
resource_registry:
  My::Simple::Template: %s
'''

validate_template = '''heat_template_version: asdf-no-such-version '''


class TestStack(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestStack, self).setUp()
        if not self.user_cloud.has_service('orchestration'):
            self.skipTest('Orchestration service not supported by cloud')

    def _cleanup_stack(self):
        self.user_cloud.delete_stack(self.stack_name, wait=True)
        self.assertIsNone(self.user_cloud.get_stack(self.stack_name))

    def test_stack_validation(self):
        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(validate_template.encode('utf-8'))
        test_template.close()
        stack_name = self.getUniqueString('validate_template')
        self.assertRaises(exc.OpenStackCloudException,
                          self.user_cloud.create_stack,
                          name=stack_name,
                          template_file=test_template.name)

    def test_stack_simple(self):
        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        test_template.close()
        self.stack_name = self.getUniqueString('simple_stack')
        self.addCleanup(self._cleanup_stack)
        stack = self.user_cloud.create_stack(
            name=self.stack_name,
            template_file=test_template.name,
            wait=True)

        # assert expected values in stack
        self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        rand = stack['outputs'][0]['output_value']
        self.assertEqual(10, len(rand))

        # assert get_stack matches returned create_stack
        stack = self.user_cloud.get_stack(self.stack_name)
        self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        self.assertEqual(rand, stack['outputs'][0]['output_value'])

        # assert stack is in list_stacks
        stacks = self.user_cloud.list_stacks()
        stack_ids = [s['id'] for s in stacks]
        self.assertIn(stack['id'], stack_ids)

        # update with no changes
        stack = self.user_cloud.update_stack(
            self.stack_name,
            template_file=test_template.name,
            wait=True)

        # assert no change in updated stack
        self.assertEqual('UPDATE_COMPLETE', stack['stack_status'])
        rand = stack['outputs'][0]['output_value']
        self.assertEqual(rand, stack['outputs'][0]['output_value'])

        # update with changes
        stack = self.user_cloud.update_stack(
            self.stack_name,
            template_file=test_template.name,
            wait=True,
            length=12)

        # assert changed output in updated stack
        stack = self.user_cloud.get_stack(self.stack_name)
        self.assertEqual('UPDATE_COMPLETE', stack['stack_status'])
        new_rand = stack['outputs'][0]['output_value']
        self.assertNotEqual(rand, new_rand)
        self.assertEqual(12, len(new_rand))

    def test_stack_nested(self):

        test_template = tempfile.NamedTemporaryFile(
            suffix='.yaml', delete=False)
        test_template.write(root_template.encode('utf-8'))
        test_template.close()

        simple_tmpl = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
        simple_tmpl.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        simple_tmpl.close()

        env = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
        expanded_env = environment % simple_tmpl.name
        env.write(expanded_env.encode('utf-8'))
        env.close()

        self.stack_name = self.getUniqueString('nested_stack')
        self.addCleanup(self._cleanup_stack)
        stack = self.user_cloud.create_stack(
            name=self.stack_name,
            template_file=test_template.name,
            environment_files=[env.name],
            wait=True)

        # assert expected values in stack
        self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        rands = stack['outputs'][0]['output_value']
        self.assertEqual(['0', '1', '2', '3', '4'], sorted(rands.keys()))
        for rand in rands.values():
            self.assertEqual(10, len(rand))
