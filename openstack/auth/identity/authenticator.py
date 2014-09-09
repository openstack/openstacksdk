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

from openstack.auth.identity import v2
from openstack.auth.identity import v3
from openstack import exceptions


def create(username=None, password=None, token=None, auth_url=None,
           version=None, project_name=None, domain_name=None,
           project_domain_name=None, user_domain_name=None):
    """Temporary code for creating an authenticator

    This is temporary code to create an authenticator.  This code will be
    removed in the future.

    :param string username: User name for authentication.
    :param string password: Password associated with the user.
    :param string token: Authentication token to use if available.
    :param string auth_url: The URL to use for authentication.
    :param string version: Version of authentication to use.
    :param string project_name: Project name to athenticate.
    :param string domain_name: Domain name to athenticate.
    :param string project_domain_name: Project domain name to athenticate.
    :param string user_domain_name: User domain name to athenticate.

    :returns string: An authenticator.
    """
    if auth_url is None:
        msg = ("auth_url wasn't provided.")
        raise exceptions.AuthorizationFailure(msg)

    endpoint_version = auth_url.split('v')[-1]
    if version is None:
        version = endpoint_version

    version = version.lower().replace('v', '')
    version = version.split('.')[0]
    if version == '3':
        args = {'user_name': username, 'password': password}
        if project_name:
            args['project_name'] = project_name
        if domain_name:
            args['domain_name'] = domain_name
        if project_domain_name:
            args['project_domain_name'] = project_domain_name
        if user_domain_name:
            args['user_domain_name'] = user_domain_name
        if token:
            args['token'] = token
        return v3.Auth(auth_url, **args)
    elif version == '2':
        args = {'user_name': username, 'password': password}
        if project_name:
            args['project_name'] = project_name
        if token:
            args['token'] = token
        return v2.Auth(auth_url, **args)
    msg = ("No support for identity version: %s" % version)
    raise exceptions.NoMatchingPlugin(msg)
