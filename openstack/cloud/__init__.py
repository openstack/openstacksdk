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

import keystoneauth1.exceptions

from openstack._log import enable_logging  # noqa
from openstack.cloud.exc import *  # noqa
from openstack.cloud.openstackcloud import OpenStackCloud


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
