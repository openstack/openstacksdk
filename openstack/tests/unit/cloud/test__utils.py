# -*- coding: utf-8 -*-

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

import random
import string
import tempfile
from uuid import uuid4

import mock
import testtools

from openstack.cloud import _utils
from openstack.cloud import exc
from openstack.tests.unit import base


RANGE_DATA = [
    dict(id=1, key1=1, key2=5),
    dict(id=2, key1=1, key2=20),
    dict(id=3, key1=2, key2=10),
    dict(id=4, key1=2, key2=30),
    dict(id=5, key1=3, key2=40),
    dict(id=6, key1=3, key2=40),
]


class TestUtils(base.TestCase):

    def test__filter_list_name_or_id(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'donald', None)
        self.assertEqual([el1], ret)

    def test__filter_list_name_or_id_special(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto[2017-01-10]')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'pluto[2017-01-10]', None)
        self.assertEqual([el2], ret)

    def test__filter_list_name_or_id_partial_bad(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto[2017-01-10]')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'pluto[2017-01]', None)
        self.assertEqual([], ret)

    def test__filter_list_name_or_id_partial_glob(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto[2017-01-10]')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'pluto*', None)
        self.assertEqual([el2], ret)

    def test__filter_list_name_or_id_non_glob_glob(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto[2017-01-10]')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'pluto', None)
        self.assertEqual([], ret)

    def test__filter_list_name_or_id_glob(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto')
        el3 = dict(id=200, name='pluto-2')
        data = [el1, el2, el3]
        ret = _utils._filter_list(data, 'pluto*', None)
        self.assertEqual([el2, el3], ret)

    def test__filter_list_name_or_id_glob_not_found(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto')
        el3 = dict(id=200, name='pluto-2')
        data = [el1, el2, el3]
        ret = _utils._filter_list(data, 'q*', None)
        self.assertEqual([], ret)

    def test__filter_list_unicode(self):
        el1 = dict(id=100, name=u'中文', last='duck',
                   other=dict(category='duck', financial=dict(status='poor')))
        el2 = dict(id=200, name=u'中文', last='trump',
                   other=dict(category='human', financial=dict(status='rich')))
        el3 = dict(id=300, name='donald', last='ronald mac',
                   other=dict(category='clown', financial=dict(status='rich')))
        data = [el1, el2, el3]
        ret = _utils._filter_list(
            data, u'中文',
            {'other': {
                'financial': {'status': 'rich'}
            }})
        self.assertEqual([el2], ret)

    def test__filter_list_filter(self):
        el1 = dict(id=100, name='donald', other='duck')
        el2 = dict(id=200, name='donald', other='trump')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'donald', {'other': 'duck'})
        self.assertEqual([el1], ret)

    def test__filter_list_filter_jmespath(self):
        el1 = dict(id=100, name='donald', other='duck')
        el2 = dict(id=200, name='donald', other='trump')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'donald', "[?other == `duck`]")
        self.assertEqual([el1], ret)

    def test__filter_list_dict1(self):
        el1 = dict(id=100, name='donald', last='duck',
                   other=dict(category='duck'))
        el2 = dict(id=200, name='donald', last='trump',
                   other=dict(category='human'))
        el3 = dict(id=300, name='donald', last='ronald mac',
                   other=dict(category='clown'))
        data = [el1, el2, el3]
        ret = _utils._filter_list(
            data, 'donald', {'other': {'category': 'clown'}})
        self.assertEqual([el3], ret)

    def test__filter_list_dict2(self):
        el1 = dict(id=100, name='donald', last='duck',
                   other=dict(category='duck', financial=dict(status='poor')))
        el2 = dict(id=200, name='donald', last='trump',
                   other=dict(category='human', financial=dict(status='rich')))
        el3 = dict(id=300, name='donald', last='ronald mac',
                   other=dict(category='clown', financial=dict(status='rich')))
        data = [el1, el2, el3]
        ret = _utils._filter_list(
            data, 'donald',
            {'other': {
                'financial': {'status': 'rich'}
            }})
        self.assertEqual([el2, el3], ret)

    def test_safe_dict_min_ints(self):
        """Test integer comparison"""
        data = [{'f1': 3}, {'f1': 2}, {'f1': 1}]
        retval = _utils.safe_dict_min('f1', data)
        self.assertEqual(1, retval)

    def test_safe_dict_min_strs(self):
        """Test integer as strings comparison"""
        data = [{'f1': '3'}, {'f1': '2'}, {'f1': '1'}]
        retval = _utils.safe_dict_min('f1', data)
        self.assertEqual(1, retval)

    def test_safe_dict_min_None(self):
        """Test None values"""
        data = [{'f1': 3}, {'f1': None}, {'f1': 1}]
        retval = _utils.safe_dict_min('f1', data)
        self.assertEqual(1, retval)

    def test_safe_dict_min_key_missing(self):
        """Test missing key for an entry still works"""
        data = [{'f1': 3}, {'x': 2}, {'f1': 1}]
        retval = _utils.safe_dict_min('f1', data)
        self.assertEqual(1, retval)

    def test_safe_dict_min_key_not_found(self):
        """Test key not found in any elements returns None"""
        data = [{'f1': 3}, {'f1': 2}, {'f1': 1}]
        retval = _utils.safe_dict_min('doesnotexist', data)
        self.assertIsNone(retval)

    def test_safe_dict_min_not_int(self):
        """Test non-integer key value raises OSCE"""
        data = [{'f1': 3}, {'f1': "aaa"}, {'f1': 1}]
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Search for minimum value failed. "
            "Value for f1 is not an integer: aaa"
        ):
            _utils.safe_dict_min('f1', data)

    def test_safe_dict_max_ints(self):
        """Test integer comparison"""
        data = [{'f1': 3}, {'f1': 2}, {'f1': 1}]
        retval = _utils.safe_dict_max('f1', data)
        self.assertEqual(3, retval)

    def test_safe_dict_max_strs(self):
        """Test integer as strings comparison"""
        data = [{'f1': '3'}, {'f1': '2'}, {'f1': '1'}]
        retval = _utils.safe_dict_max('f1', data)
        self.assertEqual(3, retval)

    def test_safe_dict_max_None(self):
        """Test None values"""
        data = [{'f1': 3}, {'f1': None}, {'f1': 1}]
        retval = _utils.safe_dict_max('f1', data)
        self.assertEqual(3, retval)

    def test_safe_dict_max_key_missing(self):
        """Test missing key for an entry still works"""
        data = [{'f1': 3}, {'x': 2}, {'f1': 1}]
        retval = _utils.safe_dict_max('f1', data)
        self.assertEqual(3, retval)

    def test_safe_dict_max_key_not_found(self):
        """Test key not found in any elements returns None"""
        data = [{'f1': 3}, {'f1': 2}, {'f1': 1}]
        retval = _utils.safe_dict_max('doesnotexist', data)
        self.assertIsNone(retval)

    def test_safe_dict_max_not_int(self):
        """Test non-integer key value raises OSCE"""
        data = [{'f1': 3}, {'f1': "aaa"}, {'f1': 1}]
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Search for maximum value failed. "
            "Value for f1 is not an integer: aaa"
        ):
            _utils.safe_dict_max('f1', data)

    def test_parse_range_None(self):
        self.assertIsNone(_utils.parse_range(None))

    def test_parse_range_invalid(self):
        self.assertIsNone(_utils.parse_range("<invalid"))

    def test_parse_range_int_only(self):
        retval = _utils.parse_range("1024")
        self.assertIsInstance(retval, tuple)
        self.assertIsNone(retval[0])
        self.assertEqual(1024, retval[1])

    def test_parse_range_lt(self):
        retval = _utils.parse_range("<1024")
        self.assertIsInstance(retval, tuple)
        self.assertEqual("<", retval[0])
        self.assertEqual(1024, retval[1])

    def test_parse_range_gt(self):
        retval = _utils.parse_range(">1024")
        self.assertIsInstance(retval, tuple)
        self.assertEqual(">", retval[0])
        self.assertEqual(1024, retval[1])

    def test_parse_range_le(self):
        retval = _utils.parse_range("<=1024")
        self.assertIsInstance(retval, tuple)
        self.assertEqual("<=", retval[0])
        self.assertEqual(1024, retval[1])

    def test_parse_range_ge(self):
        retval = _utils.parse_range(">=1024")
        self.assertIsInstance(retval, tuple)
        self.assertEqual(">=", retval[0])
        self.assertEqual(1024, retval[1])

    def test_range_filter_min(self):
        retval = _utils.range_filter(RANGE_DATA, "key1", "min")
        self.assertIsInstance(retval, list)
        self.assertEqual(2, len(retval))
        self.assertEqual(RANGE_DATA[:2], retval)

    def test_range_filter_max(self):
        retval = _utils.range_filter(RANGE_DATA, "key1", "max")
        self.assertIsInstance(retval, list)
        self.assertEqual(2, len(retval))
        self.assertEqual(RANGE_DATA[-2:], retval)

    def test_range_filter_range(self):
        retval = _utils.range_filter(RANGE_DATA, "key1", "<3")
        self.assertIsInstance(retval, list)
        self.assertEqual(4, len(retval))
        self.assertEqual(RANGE_DATA[:4], retval)

    def test_range_filter_exact(self):
        retval = _utils.range_filter(RANGE_DATA, "key1", "2")
        self.assertIsInstance(retval, list)
        self.assertEqual(2, len(retval))
        self.assertEqual(RANGE_DATA[2:4], retval)

    def test_range_filter_invalid_int(self):
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Invalid range value: <1A0"
        ):
            _utils.range_filter(RANGE_DATA, "key1", "<1A0")

    def test_range_filter_invalid_op(self):
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Invalid range value: <>100"
        ):
            _utils.range_filter(RANGE_DATA, "key1", "<>100")

    def test_file_segment(self):
        file_size = 4200
        content = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits)
            for _ in range(file_size)).encode('latin-1')
        self.imagefile = tempfile.NamedTemporaryFile(delete=False)
        self.imagefile.write(content)
        self.imagefile.close()

        segments = self.cloud._get_file_segments(
            endpoint='test_container/test_image',
            filename=self.imagefile.name,
            file_size=file_size,
            segment_size=1000)
        self.assertEqual(len(segments), 5)
        segment_content = b''
        for (index, (name, segment)) in enumerate(segments.items()):
            self.assertEqual(
                'test_container/test_image/{index:0>6}'.format(index=index),
                name)
            segment_content += segment.read()
        self.assertEqual(content, segment_content)

    def test_get_entity_pass_object(self):
        obj = mock.Mock(id=uuid4().hex)
        self.cloud.use_direct_get = True
        self.assertEqual(obj, _utils._get_entity(self.cloud, '', obj, {}))

    def test_get_entity_pass_dict(self):
        d = dict(id=uuid4().hex)
        self.cloud.use_direct_get = True
        self.assertEqual(d, _utils._get_entity(self.cloud, '', d, {}))

    def test_get_entity_no_use_direct_get(self):
        # test we are defaulting to the search_<resource> methods
        # if the use_direct_get flag is set to False(default).
        uuid = uuid4().hex
        resource = 'network'
        func = 'search_%ss' % resource
        filters = {}
        with mock.patch.object(self.cloud, func) as search:
            _utils._get_entity(self.cloud, resource, uuid, filters)
            search.assert_called_once_with(uuid, filters)

    def test_get_entity_no_uuid_like(self):
        # test we are defaulting to the search_<resource> methods
        # if the name_or_id param is a name(string) but not a uuid.
        self.cloud.use_direct_get = True
        name = 'name_no_uuid'
        resource = 'network'
        func = 'search_%ss' % resource
        filters = {}
        with mock.patch.object(self.cloud, func) as search:
            _utils._get_entity(self.cloud, resource, name, filters)
            search.assert_called_once_with(name, filters)

    def test_get_entity_pass_uuid(self):
        uuid = uuid4().hex
        self.cloud.use_direct_get = True
        resources = ['flavor', 'image', 'volume', 'network',
                     'subnet', 'port', 'floating_ip', 'security_group']
        for r in resources:
            f = 'get_%s_by_id' % r
            with mock.patch.object(self.cloud, f) as get:
                _utils._get_entity(self.cloud, r, uuid, {})
                get.assert_called_once_with(uuid)

    def test_get_entity_pass_search_methods(self):
        self.cloud.use_direct_get = True
        resources = ['flavor', 'image', 'volume', 'network',
                     'subnet', 'port', 'floating_ip', 'security_group']
        filters = {}
        name = 'name_no_uuid'
        for r in resources:
            f = 'search_%ss' % r
            with mock.patch.object(self.cloud, f) as search:
                _utils._get_entity(self.cloud, r, name, {})
                search.assert_called_once_with(name, filters)

    def test_get_entity_get_and_search(self):
        resources = ['flavor', 'image', 'volume', 'network',
                     'subnet', 'port', 'floating_ip', 'security_group']
        for r in resources:
            self.assertTrue(hasattr(self.cloud, 'get_%s_by_id' % r))
            self.assertTrue(hasattr(self.cloud, 'search_%ss' % r))
