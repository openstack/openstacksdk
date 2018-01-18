# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    'connect',
    'enable_logging',
]

import warnings

import keystoneauth1.exceptions
import requestsexceptions

from openstack._log import enable_logging  # noqa
from openstack.cloud.exc import *  # noqa
# TODO(shade) These two want to be removed before we make a release
from openstack.cloud.openstackcloud import OpenStackCloud
from openstack.cloud.operatorcloud import OperatorCloud
import openstack.connection

if requestsexceptions.SubjectAltNameWarning:
    warnings.filterwarnings(
        'ignore', category=requestsexceptions.SubjectAltNameWarning)


def _get_openstack_config(app_name=None, app_version=None):
    import openstack.config
    return openstack.config.OpenStackConfig(
        app_name=app_name, app_version=app_version)


# TODO(shade) This wants to be remove before we make a release.
def openstack_clouds(
        config=None, debug=False, cloud=None, strict=False,
        app_name=None, app_version=None):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        if cloud is None:
            return [
                OpenStackCloud(
                    cloud=f.name, debug=debug,
                    cloud_config=cloud_region,
                    strict=strict)
                for cloud_region in config.get_all()
            ]
        else:
            return [
                OpenStackCloud(
                    cloud=f.name, debug=debug,
                    cloud_config=cloud_region,
                    strict=strict)
                for cloud_region in config.get_all()
                if cloud_region.name == cloud
            ]
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))


# TODO(shade) This wants to be removed before we make a release.
def openstack_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_region = config.get_one(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OpenStackCloud(cloud_config=cloud_region, strict=strict)


# TODO(shade) This wants to be removed before we make a release.
def operator_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_region = config.get_one(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OperatorCloud(cloud_config=cloud_region, strict=strict)


def connect(*args, **kwargs):
    """Create a `openstack.connection.Connection`."""
    return openstack.connection.Connection(*args, **kwargs)


def connect_all(config=None, app_name=None, app_version=None):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        return [
            openstack.connection.Connection(config=cloud_region)
            for cloud_region in config.get_all()
        ]
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
