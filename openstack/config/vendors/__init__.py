# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
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

import glob
import json
import os

from six.moves import urllib
import requests
import yaml

from openstack.config import _util
from openstack import exceptions

_VENDORS_PATH = os.path.dirname(os.path.realpath(__file__))
_VENDOR_DEFAULTS = {}
_WELL_KNOWN_PATH = "{scheme}://{netloc}/.well-known/openstack/api"


def _get_vendor_defaults():
    global _VENDOR_DEFAULTS
    if not _VENDOR_DEFAULTS:
        for vendor in glob.glob(os.path.join(_VENDORS_PATH, '*.yaml')):
            with open(vendor, 'r') as f:
                vendor_data = yaml.safe_load(f)
                _VENDOR_DEFAULTS[vendor_data['name']] = vendor_data['profile']
        for vendor in glob.glob(os.path.join(_VENDORS_PATH, '*.json')):
            with open(vendor, 'r') as f:
                vendor_data = json.load(f)
                _VENDOR_DEFAULTS[vendor_data['name']] = vendor_data['profile']
    return _VENDOR_DEFAULTS


def get_profile(profile_name):
    vendor_defaults = _get_vendor_defaults()
    if profile_name in vendor_defaults:
        return vendor_defaults[profile_name].copy()
    profile_url = urllib.parse.urlparse(profile_name)
    if not profile_url.netloc:
        # This isn't a url, and we already don't have it.
        return
    well_known_url = _WELL_KNOWN_PATH.format(
        scheme=profile_url.scheme,
        netloc=profile_url.netloc,
    )
    response = requests.get(well_known_url)
    if not response.ok:
        raise exceptions.ConfigException(
            "{profile_name} is a remote profile that could not be fetched:"
            " {status_code} {reason}".format(
                profile_name=profile_name,
                status_code=response.status_code,
                reason=response.reason))
        vendor_defaults[profile_name] = None
        return
    vendor_data = response.json()
    name = vendor_data['name']
    # Merge named and url cloud config, but make named config override the
    # config from the cloud so that we can supply local overrides if needed.
    profile = _util.merge_clouds(
        vendor_data['profile'],
        vendor_defaults.get(name, {}))
    # If there is (or was) a profile listed in a named config profile, it
    # might still be here. We just merged in content from a URL though, so
    # pop the key to prevent doing it again in the future.
    profile.pop('profile', None)
    # Save the data under both names so we don't reprocess this, no matter
    # how we're called.
    vendor_defaults[profile_name] = profile
    vendor_defaults[name] = profile
    return profile
