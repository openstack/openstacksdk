# Copyright 2020 Red Hat, Inc.
#
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
import tempfile
import textwrap

from openstack.config import loader
from openstack import exceptions
from openstack.tests.unit.config import base

FILES = {
    'yaml': textwrap.dedent('''
        foo: bar
        baz:
            - 1
            - 2
            - 3
    '''),
    'json': textwrap.dedent('''
        {
            "foo": "bar",
            "baz": [
                1,
                2,
                3
            ]
        }
    '''),
    'txt': textwrap.dedent('''
        foo
        bar baz
        test
            one two
    '''),
}


class TestLoader(base.TestCase):

    def test_base_load_yaml_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tested_files = []
            for key, value in FILES.items():
                fn = os.path.join(tmpdir, 'file.{ext}'.format(ext=key))
                with open(fn, 'w+') as fp:
                    fp.write(value)
                tested_files.append(fn)

            path, result = loader.OpenStackConfig()._load_yaml_json_file(
                tested_files)
            # NOTE(hberaud): Prefer to test path rather than file because
            # our FILES var is a dict so results are appened
            # without keeping the initial order (python 3.5)
            self.assertEqual(tmpdir, os.path.dirname(path))

    def test__load_yaml_json_file_without_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tested_files = []
            for key, value in FILES.items():
                if key == 'json':
                    continue
                fn = os.path.join(tmpdir, 'file.{ext}'.format(ext=key))
                with open(fn, 'w+') as fp:
                    fp.write(value)
                tested_files.append(fn)

            path, result = loader.OpenStackConfig()._load_yaml_json_file(
                tested_files)
            # NOTE(hberaud): Prefer to test path rather than file because
            # our FILES var is a dict so results are appened
            # without keeping the initial order (python 3.5)
            self.assertEqual(tmpdir, os.path.dirname(path))

    def test__load_yaml_json_file_without_json_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tested_files = []
            fn = os.path.join(tmpdir, 'file.txt')
            with open(fn, 'w+') as fp:
                fp.write(FILES['txt'])
            tested_files.append(fn)

            path, result = loader.OpenStackConfig()._load_yaml_json_file(
                tested_files)
            self.assertEqual(fn, path)

    def test__load_yaml_json_file_without_perm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tested_files = []
            fn = os.path.join(tmpdir, 'file.txt')
            with open(fn, 'w+') as fp:
                fp.write(FILES['txt'])
            os.chmod(fn, 222)
            tested_files.append(fn)

            path, result = loader.OpenStackConfig()._load_yaml_json_file(
                tested_files)
            self.assertEqual(None, path)

    def test__load_yaml_json_file_nonexisting(self):
        tested_files = []
        fn = os.path.join('/fake', 'file.txt')
        tested_files.append(fn)

        path, result = loader.OpenStackConfig()._load_yaml_json_file(
            tested_files)
        self.assertEqual(None, path)


class TestFixArgv(base.TestCase):
    def test_no_changes(self):
        argv = ['-a', '-b', '--long-arg', '--multi-value', 'key1=value1',
                '--multi-value', 'key2=value2']
        expected = argv[:]
        loader._fix_argv(argv)
        self.assertEqual(expected, argv)

    def test_replace(self):
        argv = ['-a', '-b', '--long-arg', '--multi_value', 'key1=value1',
                '--multi_value', 'key2=value2']
        expected = ['-a', '-b', '--long-arg', '--multi-value', 'key1=value1',
                    '--multi-value', 'key2=value2']
        loader._fix_argv(argv)
        self.assertEqual(expected, argv)

    def test_mix(self):
        argv = ['-a', '-b', '--long-arg', '--multi_value', 'key1=value1',
                '--multi-value', 'key2=value2']
        self.assertRaises(exceptions.ConfigException,
                          loader._fix_argv, argv)
