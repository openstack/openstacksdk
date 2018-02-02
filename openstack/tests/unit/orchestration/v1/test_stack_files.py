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

import mock
from openstack.tests.unit import base

from openstack.orchestration.v1 import stack_files as sf
from openstack import resource

FAKE = {
    'stack_id': 'ID',
    'stack_name': 'NAME'
}


class TestStackFiles(base.TestCase):

    def test_basic(self):
        sot = sf.StackFiles()
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = sf.StackFiles(**FAKE)
        self.assertEqual(FAKE['stack_id'], sot.stack_id)
        self.assertEqual(FAKE['stack_name'], sot.stack_name)

    @mock.patch.object(resource.Resource, '_prepare_request')
    def test_get(self, mock_prepare_request):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value={'file': 'file-content'})

        sess = mock.Mock()
        sess.get = mock.Mock(return_value=resp)

        sot = sf.StackFiles(**FAKE)
        sot.service = mock.Mock()

        req = mock.MagicMock()
        req.url = ('/stacks/%(stack_name)s/%(stack_id)s/files' %
                   {'stack_name': FAKE['stack_name'],
                    'stack_id': FAKE['stack_id']})
        mock_prepare_request.return_value = req

        files = sot.get(sess)

        sess.get.assert_called_once_with(req.url)
        self.assertEqual({'file': 'file-content'}, files)
