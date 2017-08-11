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

import logging
import warnings

import keystoneauth1.exceptions
import pbr.version
import requestsexceptions

from openstack import _log
from openstack.cloud.exc import *  # noqa
from openstack.cloud.openstackcloud import OpenStackCloud
from openstack.cloud.operatorcloud import OperatorCloud
import openstack.connection

__version__ = pbr.version.VersionInfo('openstacksdk').version_string()

if requestsexceptions.SubjectAltNameWarning:
    warnings.filterwarnings(
        'ignore', category=requestsexceptions.SubjectAltNameWarning)


def _get_openstack_config(app_name=None, app_version=None):
    import openstack.config
    # Protect against older versions of os-client-config that don't expose this
    try:
        return openstack.config.OpenStackConfig(
            app_name=app_name, app_version=app_version)
    except Exception:
        return openstack.config.OpenStackConfig()


def simple_logging(debug=False, http_debug=False):
    if http_debug:
        debug = True
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    if http_debug:
        # Enable HTTP level tracing
        log = _log.setup_logging('keystoneauth')
        log.addHandler(logging.StreamHandler())
        log.setLevel(log_level)
        # We only want extra shade HTTP tracing in http debug mode
        log = _log.setup_logging('openstack.cloud.http')
        log.setLevel(log_level)
    else:
        # We only want extra shade HTTP tracing in http debug mode
        log = _log.setup_logging('openstack.cloud.http')
        log.setLevel(logging.WARNING)
    log = _log.setup_logging('openstack.cloud')
    log.addHandler(logging.StreamHandler())
    log.setLevel(log_level)
    # Suppress warning about keystoneauth loggers
    log = _log.setup_logging('keystoneauth.identity.base')
    log = _log.setup_logging('keystoneauth.identity.generic.base')


# TODO(shade) Document this and add some examples
# TODO(shade) This wants to be renamed before we make a release.
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
                    cloud_config=f,
                    strict=strict,
                    **f.config)
                for f in config.get_all_clouds()
            ]
        else:
            return [
                OpenStackCloud(
                    cloud=f.name, debug=debug,
                    cloud_config=f,
                    strict=strict,
                    **f.config)
                for f in config.get_all_clouds()
                if f.name == cloud
            ]
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))


# TODO(shade) This wants to be renamed before we make a release - there is
# ultimately no reason to have an openstack_cloud and a connect
# factory function - but we have a few steps to go first and this is used
# in the imported tests from shade.
def openstack_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OpenStackCloud(cloud_config=cloud_config, strict=strict)


# TODO(shade) This wants to be renamed before we make a release - there is
# ultimately no reason to have an operator_cloud and a connect
# factory function - but we have a few steps to go first and this is used
# in the imported tests from shade.
def operator_cloud(
        config=None, strict=False, app_name=None, app_version=None, **kwargs):
    if not config:
        config = _get_openstack_config(app_name, app_version)
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OperatorCloud(cloud_config=cloud_config, strict=strict)


def connect(self, *args, **kwargs):
    """Create a `openstack.connection.Connection`."""
    return openstack.connection.Connection(*args, **kwargs)
