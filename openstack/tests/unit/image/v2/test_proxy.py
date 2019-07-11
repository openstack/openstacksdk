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
import requests

from openstack import exceptions
from openstack.image.v2 import _proxy
from openstack.image.v2 import image
from openstack.image.v2 import member
from openstack.image.v2 import schema
from openstack.image.v2 import task
from openstack.image.v2 import service_info as si
from openstack.tests.unit.image.v2 import test_image as fake_image
from openstack.tests.unit import test_proxy_base

EXAMPLE = fake_image.EXAMPLE


class FakeResponse(object):
    def __init__(self, response, status_code=200, headers=None):
        self.body = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)

    def json(self):
        return self.body


class TestImageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestImageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_image_import_no_required_attrs(self):
        # container_format and disk_format are required attrs of the image
        existing_image = image.Image(id="id")
        self.assertRaises(exceptions.InvalidRequest,
                          self.proxy.import_image,
                          existing_image)

    def test_image_import(self):
        original_image = image.Image(**EXAMPLE)
        self._verify("openstack.image.v2.image.Image.import_image",
                     self.proxy.import_image,
                     method_args=[original_image, "method", "uri"],
                     expected_kwargs={"method": "method", "store": None,
                                      "uri": "uri"})

    def test_image_upload_no_args(self):
        # container_format and disk_format are required args
        self.assertRaises(exceptions.InvalidRequest, self.proxy.upload_image)

    def test_image_upload(self):
        # NOTE: This doesn't use any of the base class verify methods
        # because it ends up making two separate calls to complete the
        # operation.
        created_image = mock.Mock(spec=image.Image(id="id"))

        self.proxy._create = mock.Mock()
        self.proxy._create.return_value = created_image

        rv = self.proxy.upload_image(data="data", container_format="x",
                                     disk_format="y", name="z")

        self.proxy._create.assert_called_with(image.Image,
                                              container_format="x",
                                              disk_format="y",
                                              name="z")
        created_image.upload.assert_called_with(self.proxy)
        self.assertEqual(rv, created_image)

    def test_image_download(self):
        original_image = image.Image(**EXAMPLE)
        self._verify('openstack.image.v2.image.Image.download',
                     self.proxy.download_image,
                     method_args=[original_image],
                     method_kwargs={
                         'output': 'some_output',
                         'chunk_size': 1,
                         'stream': True
                     },
                     expected_kwargs={'output': 'some_output',
                                      'chunk_size': 1,
                                      'stream': True})

    @mock.patch("openstack.image.v2.image.Image.fetch")
    def test_image_stage(self, mock_fetch):
        img = image.Image(id="id", status="queued")
        img.stage = mock.Mock()

        self.proxy.stage_image(image=img)
        mock_fetch.assert_called()
        img.stage.assert_called_with(self.proxy)

    @mock.patch("openstack.image.v2.image.Image.fetch")
    def test_image_stage_with_data(self, mock_fetch):
        img = image.Image(id="id", status="queued")
        img.stage = mock.Mock()
        mock_fetch.return_value = img

        rv = self.proxy.stage_image(image=img, data="data")

        img.stage.assert_called_with(self.proxy)
        mock_fetch.assert_called()
        self.assertEqual(rv.data, "data")

    def test_image_stage_wrong_status(self):
        img = image.Image(id="id", status="active")
        img.stage = mock.Mock()

        self.assertRaises(
            exceptions.SDKException,
            self.proxy.stage_image,
            img,
            "data"
        )

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    @mock.patch("openstack.resource.Resource._translate_response")
    @mock.patch("openstack.proxy.Proxy._get")
    @mock.patch("openstack.image.v2.image.Image.commit")
    def test_image_update(self, mock_commit_image, mock_get_image,
                          mock_transpose):
        original_image = image.Image(**EXAMPLE)
        mock_get_image.return_value = original_image
        EXAMPLE['name'] = 'fake_name'
        updated_image = image.Image(**EXAMPLE)
        mock_commit_image.return_value = updated_image.to_dict()
        result = self.proxy.update_image(original_image,
                                         **updated_image.to_dict())
        self.assertEqual('fake_name', result.get('name'))

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, image.Image)

    def test_images(self):
        self.verify_list(self.proxy.images, image.Image)

    def test_add_tag(self):
        self._verify("openstack.image.v2.image.Image.add_tag",
                     self.proxy.add_tag,
                     method_args=["image", "tag"],
                     expected_args=["tag"])

    def test_remove_tag(self):
        self._verify("openstack.image.v2.image.Image.remove_tag",
                     self.proxy.remove_tag,
                     method_args=["image", "tag"],
                     expected_args=["tag"])

    def test_deactivate_image(self):
        self._verify("openstack.image.v2.image.Image.deactivate",
                     self.proxy.deactivate_image,
                     method_args=["image"])

    def test_reactivate_image(self):
        self._verify("openstack.image.v2.image.Image.reactivate",
                     self.proxy.reactivate_image,
                     method_args=["image"])

    def test_member_create(self):
        self.verify_create(self.proxy.add_member, member.Member,
                           method_kwargs={"image": "test_id"},
                           expected_kwargs={"image_id": "test_id"})

    def test_member_delete(self):
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.remove_member,
                      method_args=["member_id"],
                      method_kwargs={"image": "image_id",
                                     "ignore_missing": False},
                      expected_args=[member.Member],
                      expected_kwargs={"member_id": "member_id",
                                       "image_id": "image_id",
                                       "ignore_missing": False})

    def test_member_delete_ignore(self):
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.remove_member,
                      method_args=["member_id"],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member],
                      expected_kwargs={"member_id": "member_id",
                                       "image_id": "image_id",
                                       "ignore_missing": True})

    def test_member_update(self):
        self._verify2("openstack.proxy.Proxy._update",
                      self.proxy.update_member,
                      method_args=['member_id', 'image_id'],
                      expected_args=[member.Member],
                      expected_kwargs={'member_id': 'member_id',
                                       'image_id': 'image_id'})

    def test_member_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_member,
                      method_args=['member_id'],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member],
                      expected_kwargs={'member_id': 'member_id',
                                       'image_id': 'image_id'})

    def test_member_find(self):
        self._verify2("openstack.proxy.Proxy._find",
                      self.proxy.find_member,
                      method_args=['member_id'],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member, "member_id"],
                      expected_kwargs={'ignore_missing': True,
                                       'image_id': 'image_id'})

    def test_members(self):
        self.verify_list(self.proxy.members, member.Member,
                         method_args=('image_1',),
                         expected_kwargs={'image_id': 'image_1'})

    def test_images_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_images_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/images',
                                       'requires_id': False})

    def test_image_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_image_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/image',
                                       'requires_id': False})

    def test_members_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_members_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/members',
                                       'requires_id': False})

    def test_member_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_member_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/member',
                                       'requires_id': False})

    def test_task_get(self):
        self.verify_get(self.proxy.get_task, task.Task)

    def test_tasks(self):
        self.verify_list(self.proxy.tasks, task.Task)

    def test_task_create(self):
        self.verify_create(self.proxy.create_task, task.Task)

    def test_wait_for_task_immediate_status(self):
        status = 'success'
        res = task.Task(id='1234', status=status)

        result = self.proxy.wait_for_task(
            res, status, "failure", 0.01, 0.1)

        self.assertTrue(result, res)

    def test_wait_for_task_immediate_status_case(self):
        status = "SUCcess"
        res = task.Task(id='1234', status=status)

        result = self.proxy.wait_for_task(
            res, status, "failure", 0.01, 0.1)

        self.assertTrue(result, res)

    def test_wait_for_task_error_396(self):
        # Ensure we create a new task when we get 396 error
        res = task.Task(
            id='id', status='waiting',
            type='some_type', input='some_input', result='some_result'
        )

        mock_fetch = mock.Mock()
        mock_fetch.side_effect = [
            task.Task(
                id='id', status='failure',
                type='some_type', input='some_input', result='some_result',
                message=_proxy._IMAGE_ERROR_396
            ),
            task.Task(id='fake', status='waiting'),
            task.Task(id='fake', status='success'),
        ]

        self.proxy._create = mock.Mock()
        self.proxy._create.side_effect = [
            task.Task(id='fake', status='success')
        ]

        with mock.patch.object(task.Task,
                               'fetch', mock_fetch):

            result = self.proxy.wait_for_task(
                res, interval=0.01, wait=0.1)

            self.assertEqual('success', result.status)

            self.proxy._create.assert_called_with(
                mock.ANY,
                input=res.input,
                type=res.type)

    def test_wait_for_task_wait(self):
        res = task.Task(id='id', status='waiting')

        mock_fetch = mock.Mock()
        mock_fetch.side_effect = [
            task.Task(id='id', status='waiting'),
            task.Task(id='id', status='waiting'),
            task.Task(id='id', status='success'),
        ]

        with mock.patch.object(task.Task,
                               'fetch', mock_fetch):

            result = self.proxy.wait_for_task(
                res, interval=0.01, wait=0.1)

            self.assertEqual('success', result.status)

    def test_tasks_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_tasks_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/tasks',
                                       'requires_id': False})

    def test_task_schema_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_task_schema,
                      expected_args=[schema.Schema],
                      expected_kwargs={'base_path': '/schemas/task',
                                       'requires_id': False})

    def test_stores(self):
        self.verify_list(self.proxy.stores, si.Store)

    def test_import_info(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_import_info,
                      method_args=[],
                      method_kwargs={},
                      expected_args=[si.Import],
                      expected_kwargs={'require_id': False})
