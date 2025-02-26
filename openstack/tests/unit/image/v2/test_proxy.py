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

import io
import os.path
import tempfile
from unittest import mock

import requests

from openstack import exceptions
from openstack.image.v2 import _proxy
from openstack.image.v2 import cache as _cache
from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack.image.v2 import metadef_namespace as _metadef_namespace
from openstack.image.v2 import metadef_object as _metadef_object
from openstack.image.v2 import metadef_resource_type as _metadef_resource_type
from openstack.image.v2 import metadef_schema as _metadef_schema
from openstack.image.v2 import schema as _schema
from openstack.image.v2 import service_info as _service_info
from openstack.image.v2 import task as _task
from openstack import proxy as proxy_base
from openstack.tests.unit.image.v2 import test_image as fake_image
from openstack.tests.unit import test_proxy_base

EXAMPLE = fake_image.EXAMPLE


class FakeResponse:
    def __init__(self, response, status_code=200, headers=None):
        self.body = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)

    def json(self):
        return self.body


class TestImageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)
        self.proxy._connection = self.cloud


class TestImage(TestImageProxy):
    def test_image_import_no_required_attrs(self):
        # container_format and disk_format are required attrs of the image
        existing_image = _image.Image(id="id")
        self.assertRaises(
            exceptions.InvalidRequest,
            self.proxy.import_image,
            existing_image,
        )

    def test_image_import(self):
        original_image = _image.Image(**EXAMPLE)
        self._verify(
            "openstack.image.v2.image.Image.import_image",
            self.proxy.import_image,
            method_args=[original_image, "method"],
            method_kwargs={
                "uri": "uri",
            },
            expected_args=[self.proxy],
            expected_kwargs={
                "method": "method",
                "store": None,
                "uri": "uri",
                "remote_region": None,
                "remote_image_id": None,
                "remote_service_interface": None,
                "stores": [],
                "all_stores": None,
                "all_stores_must_succeed": None,
            },
        )

    def test_image_create_conflicting_options(self):
        exc = self.assertRaises(
            exceptions.SDKException,
            self.proxy.create_image,
            name='fake',
            filename='fake',
            data='fake',
            container='bare',
            disk_format='raw',
        )
        self.assertIn('filename and data are mutually exclusive', str(exc))

    def test_image_create(self):
        self.verify_create(
            self.proxy.create_image,
            _image.Image,
            method_kwargs={
                'name': 'fake',
                'disk_format': 'fake_dformat',
                'container_format': 'fake_cformat',
                'allow_duplicates': True,
                'is_protected': True,
            },
            expected_kwargs={
                'name': 'fake',
                'disk_format': 'fake_dformat',
                'container_format': 'fake_cformat',
                'is_protected': True,
                'owner_specified.openstack.md5': '',
                'owner_specified.openstack.object': 'images/fake',
                'owner_specified.openstack.sha256': '',
            },
        )

    def test_image_create_file_as_name(self):
        # if we pass a filename as an image name, we should upload the file
        # itself (and use the upload flow)
        with tempfile.NamedTemporaryFile() as tmpfile:
            name = os.path.basename(tmpfile.name)
            self._verify(
                'openstack.image.v2._proxy.Proxy._upload_image',
                self.proxy.create_image,
                method_kwargs={
                    'name': tmpfile.name,
                    'allow_duplicates': True,
                },
                expected_args=[
                    name,
                ],
                expected_kwargs={
                    'filename': tmpfile.name,
                    'data': None,
                    'meta': {},
                    'wait': False,
                    'timeout': 3600,
                    'validate_checksum': False,
                    'use_import': False,
                    'stores': None,
                    'all_stores': None,
                    'all_stores_must_succeed': None,
                    'disk_format': 'qcow2',
                    'container_format': 'bare',
                    'properties': {
                        'owner_specified.openstack.md5': '',
                        'owner_specified.openstack.object': f'images/{name}',
                        'owner_specified.openstack.sha256': '',
                    },
                },
            )

        # but not if we use a directory...
        with tempfile.TemporaryDirectory() as tmpdir:
            self.verify_create(
                self.proxy.create_image,
                _image.Image,
                method_kwargs={
                    'name': tmpdir,
                    'allow_duplicates': True,
                },
                expected_kwargs={
                    'container_format': 'bare',
                    'disk_format': 'qcow2',
                    'name': tmpdir,
                    'owner_specified.openstack.md5': '',
                    'owner_specified.openstack.object': f'images/{tmpdir}',
                    'owner_specified.openstack.sha256': '',
                },
            )

    def test_image_create_checksum_match(self):
        fake_image = _image.Image(
            id="fake",
            properties={
                self.proxy._IMAGE_MD5_KEY: 'fake_md5',
                self.proxy._IMAGE_SHA256_KEY: 'fake_sha256',
            },
        )
        self.proxy.find_image = mock.Mock(return_value=fake_image)

        self.proxy._upload_image = mock.Mock()

        res = self.proxy.create_image(
            name='fake', md5='fake_md5', sha256='fake_sha256'
        )
        self.assertEqual(fake_image, res)
        self.proxy._upload_image.assert_not_called()

    def test_image_create_checksum_mismatch(self):
        fake_image = _image.Image(
            id="fake",
            properties={
                self.proxy._IMAGE_MD5_KEY: 'fake_md5',
                self.proxy._IMAGE_SHA256_KEY: 'fake_sha256',
            },
        )
        self.proxy.find_image = mock.Mock(return_value=fake_image)

        self.proxy._upload_image = mock.Mock()

        self.proxy.create_image(
            name='fake', data=b'fake', md5='fake2_md5', sha256='fake2_sha256'
        )
        self.proxy._upload_image.assert_called()

    def test_image_create_allow_duplicates_find_not_called(self):
        self.proxy.find_image = mock.Mock()

        self.proxy._upload_image = mock.Mock()

        self.proxy.create_image(
            name='fake',
            data=b'fake',
            allow_duplicates=True,
        )

        self.proxy.find_image.assert_not_called()

    def test_image_create_validate_checksum_data_binary(self):
        """Pass real data as binary"""
        self.proxy.find_image = mock.Mock()

        self.proxy._upload_image = mock.Mock()

        self.proxy.create_image(
            name='fake',
            data=b'fake',
            validate_checksum=True,
            container='bare',
            disk_format='raw',
        )

        self.proxy.find_image.assert_called_with('fake')

        self.proxy._upload_image.assert_called_with(
            'fake',
            container_format='bare',
            disk_format='raw',
            filename=None,
            data=b'fake',
            meta={},
            properties={
                self.proxy._IMAGE_MD5_KEY: '144c9defac04969c7bfad8efaa8ea194',
                self.proxy._IMAGE_SHA256_KEY: 'b5d54c39e66671c9731b9f471e585d8262cd4f54963f0c93082d8dcf334d4c78',  # noqa: E501
                self.proxy._IMAGE_OBJECT_KEY: 'bare/fake',
            },
            timeout=3600,
            validate_checksum=True,
            use_import=False,
            stores=None,
            all_stores=None,
            all_stores_must_succeed=None,
            wait=False,
        )

    def test_image_create_validate_checksum_data_not_binary(self):
        self.assertRaises(
            exceptions.SDKException,
            self.proxy.create_image,
            name='fake',
            data=io.StringIO(),
            validate_checksum=True,
            container='bare',
            disk_format='raw',
        )

    def test_image_create_data_binary(self):
        """Pass binary file-like object"""
        self.proxy.find_image = mock.Mock()

        self.proxy._upload_image = mock.Mock()

        data = io.BytesIO(b'\0\0')

        self.proxy.create_image(
            name='fake',
            data=data,
            validate_checksum=False,
            container='bare',
            disk_format='raw',
        )

        self.proxy._upload_image.assert_called_with(
            'fake',
            container_format='bare',
            disk_format='raw',
            filename=None,
            data=data,
            meta={},
            properties={
                self.proxy._IMAGE_MD5_KEY: '',
                self.proxy._IMAGE_SHA256_KEY: '',
                self.proxy._IMAGE_OBJECT_KEY: 'bare/fake',
            },
            timeout=3600,
            validate_checksum=False,
            use_import=False,
            stores=None,
            all_stores=None,
            all_stores_must_succeed=None,
            wait=False,
        )

    def test_image_create_protected(self):
        self.proxy.find_image = mock.Mock()

        created_image = mock.Mock(spec=_image.Image(id="id"))
        self.proxy._create = mock.Mock()
        self.proxy._create.return_value = created_image
        self.proxy._create.return_value.image_import_methods = []

        created_image.upload = mock.Mock()
        created_image.upload.return_value = FakeResponse(
            response="", status_code=200
        )

        properties = {"is_protected": True}

        self.proxy.create_image(
            name="fake",
            data="data",
            container_format="bare",
            disk_format="raw",
            **properties,
        )

        args, kwargs = self.proxy._create.call_args
        self.assertEqual(kwargs["is_protected"], True)

    def test_image_create_with_stores(self):
        self.proxy.find_image = mock.Mock()
        self.proxy._upload_image = mock.Mock()

        self.proxy.create_image(
            name='fake',
            data=b'fake',
            container='bare',
            disk_format='raw',
            use_import=True,
            stores=['cinder', 'swift'],
        )

        self.proxy.find_image.assert_called_with('fake')

        self.proxy._upload_image.assert_called_with(
            'fake',
            container_format='bare',
            disk_format='raw',
            filename=None,
            data=b'fake',
            meta={},
            properties={
                self.proxy._IMAGE_MD5_KEY: '',
                self.proxy._IMAGE_SHA256_KEY: '',  # noqa: E501
                self.proxy._IMAGE_OBJECT_KEY: 'bare/fake',
            },
            timeout=3600,
            validate_checksum=False,
            use_import=True,
            stores=['cinder', 'swift'],
            all_stores=None,
            all_stores_must_succeed=None,
            wait=False,
        )

    def test_image_create_with_all_stores(self):
        self.proxy.find_image = mock.Mock()
        self.proxy._upload_image = mock.Mock()

        self.proxy.create_image(
            name='fake',
            data=b'fake',
            container='bare',
            disk_format='raw',
            use_import=True,
            all_stores=True,
            all_stores_must_succeed=True,
        )

        self.proxy.find_image.assert_called_with('fake')

        self.proxy._upload_image.assert_called_with(
            'fake',
            container_format='bare',
            disk_format='raw',
            filename=None,
            data=b'fake',
            meta={},
            properties={
                self.proxy._IMAGE_MD5_KEY: '',
                self.proxy._IMAGE_SHA256_KEY: '',  # noqa: E501
                self.proxy._IMAGE_OBJECT_KEY: 'bare/fake',
            },
            timeout=3600,
            validate_checksum=False,
            use_import=True,
            stores=None,
            all_stores=True,
            all_stores_must_succeed=True,
            wait=False,
        )

    def test_image_upload_no_args(self):
        # container_format and disk_format are required args
        self.assertRaises(exceptions.InvalidRequest, self.proxy.upload_image)

    def test_image_upload(self):
        # NOTE: This doesn't use any of the base class verify methods
        # because it ends up making two separate calls to complete the
        # operation.
        created_image = mock.Mock(spec=_image.Image(id="id"))

        self.proxy._create = mock.Mock()
        self.proxy._create.return_value = created_image

        rv = self.proxy.upload_image(
            data="data", container_format="x", disk_format="y", name="z"
        )

        self.proxy._create.assert_called_with(
            _image.Image,
            container_format="x",
            disk_format="y",
            name="z",
        )
        created_image.upload.assert_called_with(self.proxy)
        self.assertEqual(rv, created_image)

    def test_image_download(self):
        original_image = _image.Image(**EXAMPLE)
        self._verify(
            'openstack.image.v2.image.Image.download',
            self.proxy.download_image,
            method_args=[original_image],
            method_kwargs={
                'output': 'some_output',
                'chunk_size': 1,
                'stream': True,
            },
            expected_args=[self.proxy],
            expected_kwargs={
                'output': 'some_output',
                'chunk_size': 1,
                'stream': True,
            },
        )

    @mock.patch("openstack.image.v2.image.Image.fetch")
    def test_image_stage(self, mock_fetch):
        image = _image.Image(id="id", status="queued")
        image.stage = mock.Mock()

        self.proxy.stage_image(image)
        mock_fetch.assert_called()
        image.stage.assert_called_with(self.proxy)

    @mock.patch("openstack.image.v2.image.Image.fetch")
    def test_image_stage_with_data(self, mock_fetch):
        image = _image.Image(id="id", status="queued")
        image.stage = mock.Mock()
        mock_fetch.return_value = image

        rv = self.proxy.stage_image(image, data="data")

        image.stage.assert_called_with(self.proxy)
        mock_fetch.assert_called()
        self.assertEqual(rv.data, "data")

    def test_image_stage_conflicting_options(self):
        image = _image.Image(id="id", status="queued")
        image.stage = mock.Mock()

        exc = self.assertRaises(
            exceptions.SDKException,
            self.proxy.stage_image,
            image,
            filename='foo',
            data='data',
        )
        self.assertIn(
            'filename and data are mutually exclusive',
            str(exc),
        )
        image.stage.assert_not_called()

    def test_image_stage_wrong_status(self):
        image = _image.Image(id="id", status="active")
        image.stage = mock.Mock()

        exc = self.assertRaises(
            exceptions.SDKException,
            self.proxy.stage_image,
            image,
            data="data",
        )
        self.assertIn(
            'Image stage is only possible for images in the queued state.',
            str(exc),
        )
        image.stage.assert_not_called()

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, _image.Image, False)

    def test_image_delete__ignore(self):
        self.verify_delete(self.proxy.delete_image, _image.Image, True)

    def test_delete_image__from_store(self):
        store = _service_info.Store(id='fast', is_default=True)
        store.delete_image = mock.Mock()
        image = _image.Image(id="id", status="queued")

        self.proxy.delete_image(image, store=store)

        store.delete_image.assert_called_with(
            self.proxy,
            image,
            ignore_missing=True,
        )

    @mock.patch("openstack.resource.Resource._translate_response")
    @mock.patch("openstack.proxy.Proxy._get")
    @mock.patch("openstack.image.v2.image.Image.commit")
    def test_image_update(
        self, mock_commit_image, mock_get_image, mock_transpose
    ):
        original_image = _image.Image(**EXAMPLE)
        mock_get_image.return_value = original_image
        EXAMPLE['name'] = 'fake_name'
        updated_image = _image.Image(**EXAMPLE)
        mock_commit_image.return_value = updated_image.to_dict()
        result = self.proxy.update_image(
            original_image, **updated_image.to_dict()
        )
        self.assertEqual('fake_name', result.get('name'))

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, _image.Image)

    def test_images(self):
        self.verify_list(self.proxy.images, _image.Image)

    def test_add_tag(self):
        self._verify(
            "openstack.image.v2.image.Image.add_tag",
            self.proxy.add_tag,
            method_args=["image", "tag"],
            expected_args=[self.proxy, "tag"],
        )

    def test_remove_tag(self):
        self._verify(
            "openstack.image.v2.image.Image.remove_tag",
            self.proxy.remove_tag,
            method_args=["image", "tag"],
            expected_args=[self.proxy, "tag"],
        )

    def test_deactivate_image(self):
        self._verify(
            "openstack.image.v2.image.Image.deactivate",
            self.proxy.deactivate_image,
            method_args=["image"],
            expected_args=[self.proxy],
        )

    def test_reactivate_image(self):
        self._verify(
            "openstack.image.v2.image.Image.reactivate",
            self.proxy.reactivate_image,
            method_args=["image"],
            expected_args=[self.proxy],
        )


class TestMember(TestImageProxy):
    def test_member_create(self):
        self.verify_create(
            self.proxy.add_member,
            _member.Member,
            method_kwargs={"image": "test_id"},
            expected_kwargs={"image_id": "test_id"},
        )

    def test_member_delete(self):
        self._verify(
            "openstack.proxy.Proxy._delete",
            self.proxy.remove_member,
            method_args=["member_id"],
            method_kwargs={"image": "image_id", "ignore_missing": False},
            expected_args=[_member.Member, None],
            expected_kwargs={
                "member_id": "member_id",
                "image_id": "image_id",
                "ignore_missing": False,
            },
        )

    def test_member_delete_ignore(self):
        self._verify(
            "openstack.proxy.Proxy._delete",
            self.proxy.remove_member,
            method_args=["member_id"],
            method_kwargs={"image": "image_id"},
            expected_args=[_member.Member, None],
            expected_kwargs={
                "member_id": "member_id",
                "image_id": "image_id",
                "ignore_missing": True,
            },
        )

    def test_member_update(self):
        self._verify(
            "openstack.proxy.Proxy._update",
            self.proxy.update_member,
            method_args=['member_id', 'image_id'],
            expected_args=[_member.Member, None],
            expected_kwargs={'member_id': 'member_id', 'image_id': 'image_id'},
        )

    def test_member_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_member,
            method_args=['member_id'],
            method_kwargs={"image": "image_id"},
            expected_args=[_member.Member],
            expected_kwargs={'member_id': 'member_id', 'image_id': 'image_id'},
        )

    def test_member_find(self):
        self._verify(
            "openstack.proxy.Proxy._find",
            self.proxy.find_member,
            method_args=['member_id'],
            method_kwargs={"image": "image_id"},
            expected_args=[_member.Member, "member_id"],
            expected_kwargs={'ignore_missing': True, 'image_id': 'image_id'},
        )

    def test_members(self):
        self.verify_list(
            self.proxy.members,
            _member.Member,
            method_kwargs={'image': 'image_1'},
            expected_kwargs={'image_id': 'image_1'},
        )


class TestMetadefNamespace(TestImageProxy):
    def test_metadef_namespace_create(self):
        self.verify_create(
            self.proxy.create_metadef_namespace,
            _metadef_namespace.MetadefNamespace,
        )

    def test_metadef_namespace_delete(self):
        self.verify_delete(
            self.proxy.delete_metadef_namespace,
            _metadef_namespace.MetadefNamespace,
            False,
        )

    def test_metadef_namespace_delete__ignore(self):
        self.verify_delete(
            self.proxy.delete_metadef_namespace,
            _metadef_namespace.MetadefNamespace,
            True,
        )

    def test_metadef_namespace_get(self):
        self.verify_get(
            self.proxy.get_metadef_namespace,
            _metadef_namespace.MetadefNamespace,
        )

    def test_metadef_namespaces(self):
        self.verify_list(
            self.proxy.metadef_namespaces,
            _metadef_namespace.MetadefNamespace,
        )

    def test_metadef_namespace_update(self):
        # we're (intentionally) adding an additional field, 'namespace', to the
        # request body
        self.verify_update(
            self.proxy.update_metadef_namespace,
            _metadef_namespace.MetadefNamespace,
            method_kwargs={'is_protected': True},
            expected_kwargs={'namespace': 'resource_id', 'is_protected': True},
        )


class TestMetadefObject(TestImageProxy):
    def test_create_metadef_object(self):
        self.verify_create(
            self.proxy.create_metadef_object,
            _metadef_object.MetadefObject,
            method_kwargs={"namespace": "test_namespace_name"},
            expected_kwargs={"namespace_name": "test_namespace_name"},
        )

    def test_get_metadef_object(self):
        self.verify_get(
            self.proxy.get_metadef_object,
            _metadef_object.MetadefObject,
            method_kwargs={"namespace": "test_namespace_name"},
            expected_kwargs={
                "namespace_name": "test_namespace_name",
                'name': 'resource_id',
            },
            expected_args=[],
        )

    def test_metadef_objects(self):
        self.verify_list(
            self.proxy.metadef_objects,
            _metadef_object.MetadefObject,
            method_kwargs={"namespace": "test_namespace_name"},
            expected_kwargs={"namespace_name": "test_namespace_name"},
        )

    def test_update_metadef_object(self):
        self._verify(
            "openstack.proxy.Proxy._update",
            self.proxy.update_metadef_object,
            method_args=["test_metadef_object", "test_namespace_name"],
            method_kwargs={"name": "new_object"},
            expected_args=[
                _metadef_object.MetadefObject,
                'test_metadef_object',
            ],
            expected_kwargs={
                "name": "new_object",
                "namespace_name": "test_namespace_name",
            },
        )

    def test_delete_metadef_object(self):
        self.verify_delete(
            self.proxy.delete_metadef_object,
            _metadef_object.MetadefObject,
            False,
            method_kwargs={"namespace": "test_namespace_name"},
            expected_kwargs={"namespace_name": "test_namespace_name"},
        )

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_delete_all_metadef_objects(self, mock_get_resource):
        fake_object = _metadef_namespace.MetadefNamespace()
        mock_get_resource.return_value = fake_object
        self._verify(
            "openstack.image.v2.metadef_namespace.MetadefNamespace.delete_all_objects",
            self.proxy.delete_all_metadef_objects,
            method_args=['test_namespace'],
            expected_args=[self.proxy],
        )
        mock_get_resource.assert_called_once_with(
            _metadef_namespace.MetadefNamespace, 'test_namespace'
        )


class TestMetadefResourceType(TestImageProxy):
    def test_metadef_resource_types(self):
        self.verify_list(
            self.proxy.metadef_resource_types,
            _metadef_resource_type.MetadefResourceType,
        )


class TestMetadefResourceTypeAssociation(TestImageProxy):
    def test_create_metadef_resource_type_association(self):
        self.verify_create(
            self.proxy.create_metadef_resource_type_association,
            _metadef_resource_type.MetadefResourceTypeAssociation,
            method_kwargs={'metadef_namespace': 'namespace_name'},
            expected_kwargs={'namespace_name': 'namespace_name'},
        )

    def test_delete_metadef_resource_type_association(self):
        self.verify_delete(
            self.proxy.delete_metadef_resource_type_association,
            _metadef_resource_type.MetadefResourceTypeAssociation,
            False,
            method_kwargs={'metadef_namespace': 'namespace_name'},
            expected_kwargs={'namespace_name': 'namespace_name'},
        )

    def test_delete_metadef_resource_type_association_ignore(self):
        self.verify_delete(
            self.proxy.delete_metadef_resource_type_association,
            _metadef_resource_type.MetadefResourceTypeAssociation,
            True,
            method_kwargs={'metadef_namespace': 'namespace_name'},
            expected_kwargs={'namespace_name': 'namespace_name'},
        )

    def test_metadef_resource_type_associations(self):
        self.verify_list(
            self.proxy.metadef_resource_type_associations,
            _metadef_resource_type.MetadefResourceTypeAssociation,
            method_kwargs={'metadef_namespace': 'namespace_name'},
            expected_kwargs={'namespace_name': 'namespace_name'},
        )


class TestSchema(TestImageProxy):
    def test_images_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_images_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/images',
                'requires_id': False,
            },
        )

    def test_image_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_image_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/image',
                'requires_id': False,
            },
        )

    def test_members_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_members_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/members',
                'requires_id': False,
            },
        )

    def test_member_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_member_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/member',
                'requires_id': False,
            },
        )


class TestTask(TestImageProxy):
    def test_task_get(self):
        self.verify_get(self.proxy.get_task, _task.Task)

    def test_tasks(self):
        self.verify_list(self.proxy.tasks, _task.Task)

    def test_task_create(self):
        self.verify_create(self.proxy.create_task, _task.Task)

    def test_wait_for_task_immediate_status(self):
        status = 'success'
        res = _task.Task(id='1234', status=status)

        result = self.proxy.wait_for_task(res, status, "failure", 0.01, 0.1)

        self.assertEqual(res, result)

    def test_wait_for_task_immediate_status_case(self):
        status = "SUCcess"
        res = _task.Task(id='1234', status=status)

        result = self.proxy.wait_for_task(res, status, "failure", 0.01, 0.1)

        self.assertEqual(res, result)

    def test_wait_for_task_error_396(self):
        # Ensure we create a new task when we get 396 error
        res = _task.Task(
            id='id',
            status='waiting',
            type='some_type',
            input='some_input',
            result='some_result',
        )

        mock_fetch = mock.Mock()
        mock_fetch.side_effect = [
            _task.Task(
                id='id',
                status='failure',
                type='some_type',
                input='some_input',
                result='some_result',
                message=_proxy._IMAGE_ERROR_396,
            ),
            _task.Task(id='fake', status='waiting'),
            _task.Task(id='fake', status='success'),
        ]

        self.proxy._create = mock.Mock()
        self.proxy._create.side_effect = [
            _task.Task(id='fake', status='success')
        ]

        with mock.patch.object(_task.Task, 'fetch', mock_fetch):
            result = self.proxy.wait_for_task(res, interval=0.01, wait=0.5)

            self.assertEqual('success', result.status)

            self.proxy._create.assert_called_with(
                mock.ANY, input=res.input, type=res.type
            )

    def test_wait_for_task_wait(self):
        res = _task.Task(id='id', status='waiting')

        mock_fetch = mock.Mock()
        mock_fetch.side_effect = [
            _task.Task(id='id', status='waiting'),
            _task.Task(id='id', status='waiting'),
            _task.Task(id='id', status='success'),
        ]

        with mock.patch.object(_task.Task, 'fetch', mock_fetch):
            result = self.proxy.wait_for_task(res, interval=0.01, wait=0.5)

            self.assertEqual('success', result.status)

    def test_tasks_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_tasks_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/tasks',
                'requires_id': False,
            },
        )

    def test_task_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_task_schema,
            expected_args=[_schema.Schema],
            expected_kwargs={
                'base_path': '/schemas/task',
                'requires_id': False,
            },
        )


class TestMisc(TestImageProxy):
    def test_stores(self):
        self.verify_list(self.proxy.stores, _service_info.Store)

    def test_import_info(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_import_info,
            method_args=[],
            method_kwargs={},
            expected_args=[_service_info.Import],
            expected_kwargs={'requires_id': False},
        )


class TestMetadefSchema(TestImageProxy):
    def test_metadef_namespace_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_namespace_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/namespace',
                'requires_id': False,
            },
        )

    def test_metadef_namespaces_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_namespaces_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/namespaces',
                'requires_id': False,
            },
        )

    def test_metadef_resource_type_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_resource_type_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/resource_type',
                'requires_id': False,
            },
        )

    def test_metadef_resource_types_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_resource_types_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/resource_types',
                'requires_id': False,
            },
        )

    def test_metadef_object_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_object_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/object',
                'requires_id': False,
            },
        )

    def test_metadef_objects_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_objects_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/objects',
                'requires_id': False,
            },
        )

    def test_metadef_property_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_property_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/property',
                'requires_id': False,
            },
        )

    def test_metadef_properties_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_properties_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/properties',
                'requires_id': False,
            },
        )

    def test_metadef_tag_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_tag_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/tag',
                'requires_id': False,
            },
        )

    def test_metadef_tags_schema_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_metadef_tags_schema,
            expected_args=[_metadef_schema.MetadefSchema],
            expected_kwargs={
                'base_path': '/schemas/metadefs/tags',
                'requires_id': False,
            },
        )


class TestCache(TestImageProxy):
    def test_image_cache_get(self):
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_image_cache,
            expected_args=[_cache.Cache],
            expected_kwargs={'requires_id': False},
        )

    def test_cache_image_delete(self):
        self.verify_delete(
            self.proxy.cache_delete_image,
            _cache.Cache,
        )

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_image_queue(self, mock_get_resource):
        fake_cache = _cache.Cache()
        mock_get_resource.return_value = fake_cache
        self._verify(
            "openstack.image.v2.cache.Cache.queue",
            self.proxy.queue_image,
            method_args=['image-id'],
            expected_args=[self.proxy, 'image-id'],
        )
        mock_get_resource.assert_called_once_with(_cache.Cache, None)

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_image_clear_cache(self, mock_get_resource):
        fake_cache = _cache.Cache()
        mock_get_resource.return_value = fake_cache
        self._verify(
            "openstack.image.v2.cache.Cache.clear",
            self.proxy.clear_cache,
            method_args=['both'],
            expected_args=[self.proxy, 'both'],
        )
        mock_get_resource.assert_called_once_with(_cache.Cache, None)

        mock_get_resource.reset_mock()
        self._verify(
            "openstack.image.v2.cache.Cache.clear",
            self.proxy.clear_cache,
            method_args=[],
            expected_args=[self.proxy, 'both'],
        )
        mock_get_resource.assert_called_once_with(_cache.Cache, None)
