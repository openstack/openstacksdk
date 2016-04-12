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

"""
The :class:`~openstack.session.Session` overrides
:class:`~keystoneauth1.session.Session` to provide end point filtering and
mapping KSA exceptions to SDK exceptions.

"""
import re

from keystoneauth1 import exceptions as _exceptions
from keystoneauth1 import session as _session

import openstack
from openstack import exceptions

from six.moves.urllib import parse

DEFAULT_USER_AGENT = "openstacksdk/%s" % openstack.__version__
VERSION_PATTERN = re.compile('/v\d[\d.]*')


def parse_url(filt, url):
    result = parse.urlparse(url)
    path = result.path
    vstr = VERSION_PATTERN.search(path)
    if not vstr:
        return (result.scheme + "://" + result.netloc + path.rstrip('/') +
                '/' + filt.get_path())
    start, end = vstr.span()
    prefix = path[:start]
    version = '/' + filt.get_path(path[start + 1:end])
    postfix = path[end:].rstrip('/') if path[end:] else ''
    url = result.scheme + "://" + result.netloc + prefix + version + postfix
    return url


def map_exceptions(func):
    def map_exceptions_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except _exceptions.HttpError as e:
            if e.http_status == 404:
                raise exceptions.NotFoundException(
                    message=e.message, details=e.details,
                    response=e.response, request_id=e.request_id,
                    url=e.url, method=e.method,
                    http_status=e.http_status, cause=e)
            else:
                raise exceptions.HttpException(
                    message=e.message, details=e.details,
                    response=e.response, request_id=e.request_id,
                    url=e.url, method=e.method,
                    http_status=e.http_status, cause=e)
        except _exceptions.ClientException as e:
            raise exceptions.SDKException(message=e.message, cause=e)

    return map_exceptions_wrapper


class Session(_session.Session):

    def __init__(self, profile, user_agent=None, **kwargs):
        """Create a new Keystone auth session with a profile.

        :param profile: If the user has any special profiles such as the
            service name, region, version or interface, they may be provided
            in the profile object.  If no profiles are provided, the
            services that appear first in the service catalog will be used.
        :param user_agent: A User-Agent header string to use for the
                           request. If not provided, a default of
                           :attr:`~openstack.session.DEFAULT_USER_AGENT`
                           is used, which contains the openstacksdk version
                           When a non-None value is passed, it will be
                           prepended to the default.
        :type profile: :class:`~openstack.profile.Profile`
        """
        if user_agent is not None:
            self.user_agent = "%s %s" % (user_agent, DEFAULT_USER_AGENT)
        else:
            self.user_agent = DEFAULT_USER_AGENT
        super(Session, self).__init__(user_agent=self.user_agent, **kwargs)

        self.profile = profile

    def get_endpoint(self, auth=None, interface=None, **kwargs):
        """Override get endpoint to automate endpoint filtering"""

        service_type = kwargs.get('service_type')
        filt = self.profile.get_filter(service_type)
        if filt.interface is None:
            filt.interface = interface
        url = super(Session, self).get_endpoint(auth, **filt.get_filter())
        return parse_url(filt, url)

    @map_exceptions
    def request(self, *args, **kwargs):
        return super(Session, self).request(*args, **kwargs)
