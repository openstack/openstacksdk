# Copyright 2012 Nebula, Inc.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

from oslo_utils import timeutils

from openstack.auth import service_catalog as catalog


# Do not use token before expiration
BEST_BEFORE_SECONDS = 30


class AccessInfo(object):
    """Encapsulates a raw authentication token from keystone.

    Provides helper methods for extracting useful values from that token.

    """
    def __init__(self, **kwargs):
        """Construct access info."""
        self._info = kwargs

    @classmethod
    def factory(cls, resp=None, body=None, **kwargs):
        """AccessInfo factory.

        Create AccessInfo object given a successful auth response & body
        or a user-provided dict.
        """

        if body is not None or len(kwargs):
            if AccessInfoV3.is_valid(body, **kwargs):
                token = None
                if resp:
                    token = resp.headers['X-Subject-Token']
                if body:
                    return AccessInfoV3(token, **body['token'])
                else:
                    return AccessInfoV3(token, **kwargs)
            elif AccessInfoV2.is_valid(body, **kwargs):
                if body:
                    return AccessInfoV2(**body['access'])
                else:
                    return AccessInfoV2(**kwargs)
            else:
                raise NotImplementedError('Unrecognized auth response')
        else:
            return AccessInfoV2(**kwargs)

    def will_expire_soon(self, best_before=BEST_BEFORE_SECONDS):
        """Determines if expiration is about to occur.

        :return: boolean : true if expiration is within the given duration

        """
        norm_expires = timeutils.normalize_time(self.expires)
        soon = (timeutils.utcnow() + datetime.timedelta(seconds=best_before))
        return norm_expires < soon

    @classmethod
    def is_valid(cls, body, **kwargs):
        """Valid v2 or v3 token

        Determines if processing v2 or v3 token given a successful
        auth body or a user-provided dict.

        :return: boolean : true if auth body matches implementing class
        """
        raise NotImplementedError()

    def has_service_catalog(self):
        """Returns true if the authorization token has a service catalog.

        :returns: boolean
        """
        raise NotImplementedError()

    @property
    def auth_token(self):
        """Authorize token

        Returns the token_id associated with the auth request, to be used
        in headers for authenticating OpenStack API requests.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def expires(self):
        """Returns the token expiration (as datetime object)

        :returns: datetime
        """
        raise NotImplementedError()

    @property
    def username(self):
        """User name

        Returns the username associated with the authentication request.
        Follows the pattern defined in the V2 API of first looking for 'name',
        returning that if available, and falling back to 'username' if name
        is unavailable.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_id(self):
        """Returns the user id associated with the authentication request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_domain_id(self):
        """Users domain id

        Returns the domain id of the user associated with the authentication
        request.  For v2, it always returns 'default' which may be different
        from the Keystone configuration.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_domain_name(self):
        """Users domain name

        Returns the domain name of the user associated with the authentication
        request.  For v2, it always returns 'Default' which may be different
        from the Keystone configuration.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def role_names(self):
        """Role names

        Returns a list of role names of the user associated with the
        authentication request.

        :returns: a list of strings of role names
        """
        raise NotImplementedError()

    @property
    def domain_name(self):
        """Returns the domain name associated with the authentication token.

        :returns: str or None (if no domain associated with the token)
        """
        raise NotImplementedError()

    @property
    def domain_id(self):
        """Returns the domain id associated with the authentication token.

        :returns: str or None (if no domain associated with the token)
        """
        raise NotImplementedError()

    @property
    def project_name(self):
        """Returns the project name associated with the authentication request.

        :returns: str or None (if no project associated with the token)
        """
        raise NotImplementedError()

    @property
    def tenant_name(self):
        """Synonym for project_name."""
        return self.project_name

    @property
    def project_scoped(self):
        """Returns true if the authorization token was scoped to a project.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def domain_scoped(self):
        """Returns true if the authorization token was scoped to a domain.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def trust_id(self):
        """Returns the trust id associated with the authentication token.

        :returns: str or None (if no trust associated with the token)
        """
        raise NotImplementedError()

    @property
    def trust_scoped(self):
        """Delegated to a trust.

        Returns true if the authorization token was scoped as delegated in a
        trust, via the OS-TRUST v3 extension.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def project_id(self):
        """Project id.

        Returns the project ID associated with the authentication request,
        or None if the authentication request wasn't scoped to a project.

        :returns: str or None (if no project associated with the token)
        """
        raise NotImplementedError()

    @property
    def tenant_id(self):
        """Synonym for project_id."""
        return self.project_id

    @property
    def project_domain_id(self):
        """Project domain.

        Returns the domain id of the project associated with the authentication
        request.  For v2, it returns 'default' if a project is scoped or None
        which may be different from the keystone configuration.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def project_domain_name(self):
        """Project domain name.

        Returns the domain name of the project associated with the
        authentication request.  For v2, it returns 'Default' if a project is
        scoped or None  which may be different from the keystone configuration.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def version(self):
        """Returns the version of the auth token from identity service.

        :returns: str
        """
        return self._info.get('version')

    def __repr__(self):
        return str(self._info)


class AccessInfoV2(AccessInfo):
    """Object for encapsulating a raw v2 auth token from identity service."""

    def __init__(self, **kwargs):
        super(AccessInfoV2, self).__init__(**kwargs)
        self._info.update(version='v2.0')
        service_catalog = self._info['serviceCatalog']
        self.service_catalog = catalog.ServiceCatalogV2(service_catalog)

    @classmethod
    def is_valid(cls, body, **kwargs):
        if body:
            return 'access' in body
        elif kwargs:
            return kwargs.get('version') == 'v2.0'
        else:
            return False

    def has_service_catalog(self):
        return 'serviceCatalog' in self._info

    @property
    def auth_token(self):
        return self._info['token']['id']

    @property
    def expires(self):
        return timeutils.parse_isotime(self._info['token']['expires'])

    @property
    def username(self):
        user = self._info['user']
        return user.get('name', user.get('username'))

    @property
    def user_id(self):
        return self._info['user']['id']

    @property
    def user_domain_id(self):
        return 'default'

    @property
    def user_domain_name(self):
        return 'Default'

    @property
    def role_names(self):
        return [r['name'] for r in self._info['user'].get('roles', [])]

    @property
    def domain_name(self):
        return None

    @property
    def domain_id(self):
        return None

    @property
    def project_name(self):
        try:
            tenant_dict = self._info['token']['tenant']
        except KeyError:
            pass
        else:
            return tenant_dict.get('name')

        # pre grizzly
        try:
            return self._info['user']['tenantName']
        except KeyError:
            pass

        # pre diablo, keystone only provided a tenantId
        try:
            return self._info['token']['tenantId']
        except KeyError:
            pass

    @property
    def project_scoped(self):
        return 'tenant' in self._info['token']

    @property
    def domain_scoped(self):
        return False

    @property
    def trust_id(self):
        return self._info.get('trust', {}).get('id')

    @property
    def trust_scoped(self):
        return 'trust' in self._info

    @property
    def project_id(self):
        try:
            tenant_dict = self._info['token']['tenant']
        except KeyError:
            pass
        else:
            return tenant_dict.get('id')

        # pre grizzly
        try:
            return self._info['user']['tenantId']
        except KeyError:
            pass

        # pre diablo
        try:
            return self._info['token']['tenantId']
        except KeyError:
            pass

    @property
    def project_domain_id(self):
        if self.project_id:
            return 'default'

    @property
    def project_domain_name(self):
        if self.project_id:
            return 'Default'


class AccessInfoV3(AccessInfo):
    """Object for encapsulating a raw v3 auth token from identity service."""

    def __init__(self, token, **kwargs):
        super(AccessInfoV3, self).__init__(**kwargs)
        self._info.update(version='v3')
        self.service_catalog = catalog.ServiceCatalog(self._info['catalog'])
        if token:
            self._info.update(auth_token=token)

    @classmethod
    def is_valid(cls, body, **kwargs):
        if body:
            return 'token' in body
        elif kwargs:
            return kwargs.get('version') == 'v3'
        else:
            return False

    def has_service_catalog(self):
        return 'catalog' in self._info

    @property
    def auth_token(self):
        return self._info['auth_token']

    @property
    def expires(self):
        return timeutils.parse_isotime(self._info['expires_at'])

    @property
    def user_id(self):
        return self._info['user']['id']

    @property
    def user_domain_id(self):
        return self._info['user']['domain']['id']

    @property
    def user_domain_name(self):
        return self._info['user']['domain']['name']

    @property
    def role_names(self):
        return [r['name'] for r in self._info.get('roles', [])]

    @property
    def username(self):
        return self._info['user']['name']

    @property
    def domain_name(self):
        domain = self._info.get('domain')
        if domain:
            return domain['name']

    @property
    def domain_id(self):
        domain = self._info.get('domain')
        if domain:
            return domain['id']

    @property
    def project_id(self):
        project = self._info.get('project')
        if project:
            return project['id']

    @property
    def project_domain_id(self):
        project = self._info.get('project')
        if project:
            return project['domain']['id']

    @property
    def project_domain_name(self):
        project = self._info.get('project')
        if project:
            return project['domain']['name']

    @property
    def project_name(self):
        project = self._info.get('project')
        if project:
            return project['name']

    @property
    def project_scoped(self):
        return 'project' in self._info

    @property
    def domain_scoped(self):
        return 'domain' in self._info

    @property
    def trust_id(self):
        return self._info.get('OS-TRUST:trust', {}).get('id')

    @property
    def trust_scoped(self):
        return 'OS-TRUST:trust' in self._info
