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

from openstack import exceptions

from stevedore import driver


def create(auth_plugin=None, **auth_args):
    """Temporary code for creating an authenticator

    This is temporary code to create an authenticator.  This code will be
    removed in the future.

    :param string auth_plugin: Name of authentication plugin to use.
    :param auth_args: Arguments for auth plugin.

    :returns string: An authenticator.
    """

    if auth_plugin is None:
        if 'auth_url' not in auth_args:
            msg = ("auth_url was not provided.")
            raise exceptions.AuthorizationFailure(msg)
        auth_url = auth_args['auth_url']
        endpoint_version = auth_url.split('v')[-1][0]
        if endpoint_version == '2':
            auth_plugin = 'identity_v2'
        else:
            auth_plugin = 'identity_v3'

    mgr = driver.DriverManager(
        namespace="openstack.auth.plugin",
        name=auth_plugin,
        invoke_on_load=False,
    )
    plugin = mgr.driver
    valid_list = plugin.valid_options
    args = {}
    for k in valid_list:
        if k in auth_args:
            args[k] = auth_args[k]
    return plugin(**args)
