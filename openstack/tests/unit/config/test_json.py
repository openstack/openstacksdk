# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import copy
import glob
import json
import os

import jsonschema
import referencing
from testtools import content

from openstack.config import defaults
from openstack.tests.unit.config import base

_CONFIG_DIR = os.path.dirname(os.path.realpath(defaults.__file__))


def _load_schema(filename):
    with open(os.path.join(_CONFIG_DIR, filename)) as f:
        return json.load(f)


class TestConfig(base.TestCase):
    def json_diagnostics(self, exc_info):
        self.addDetail('filename', content.text_content(self.filename))
        for error in sorted(
            self.validator.iter_errors(self.json_data), key=str
        ):
            self.addDetail('jsonschema', content.text_content(str(error)))

    def test_defaults_valid_json(self):
        schema = _load_schema('schema.json')
        self.validator = jsonschema.Draft202012Validator(schema)
        self.addOnException(self.json_diagnostics)

        self.filename = os.path.join(_CONFIG_DIR, 'defaults.json')
        with open(self.filename) as f:
            self.json_data = json.load(f)

        self.assertTrue(self.validator.is_valid(self.json_data))

    def test_clouds_valid_json(self):
        # the clouds.yaml schema reuses the single-cloud schema for each
        # 'clouds' entry via a cross-file $ref, so both schemas must be
        # registered for the reference to resolve
        schema = _load_schema('schema.json')
        clouds_schema = _load_schema('clouds-schema.json')
        registry = referencing.Registry().with_resources(
            [
                (schema['$id'], referencing.Resource.from_contents(schema)),
                (
                    clouds_schema['$id'],
                    referencing.Resource.from_contents(clouds_schema),
                ),
            ]
        )
        self.validator = jsonschema.Draft202012Validator(
            clouds_schema, registry=registry
        )
        self.addOnException(self.json_diagnostics)

        # USER_CONF is the comprehensive fixture used across the config
        # tests; it exercises the top-level sections (cache, client, metrics,
        # ansible), deprecated aliases and both region entry forms
        self.filename = 'clouds-schema.json'
        self.json_data = copy.deepcopy(base.USER_CONF)

        self.assertTrue(self.validator.is_valid(self.json_data))

    def test_vendors_valid_json(self):
        _schema_path = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)),
            'vendor-schema.json',
        )
        with open(_schema_path) as f:
            schema = json.load(f)
            self.validator = jsonschema.Draft202012Validator(schema)

        self.addOnException(self.json_diagnostics)

        _vendors_path = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)), 'vendors'
        )
        for self.filename in glob.glob(os.path.join(_vendors_path, '*.json')):
            with open(self.filename) as f:
                self.json_data = json.load(f)

                self.assertTrue(self.validator.is_valid(self.json_data))
