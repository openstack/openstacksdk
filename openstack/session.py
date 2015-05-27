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
:class:`~keystoneauth1.session.Session` to provide end point filtering.

"""
import re
from six.moves.urllib import parse

from keystoneauth1 import session as _session


VERSION_PATTERN = re.compile('/v\d[\d.]*')


def parse_url(filt, url):
    result = parse.urlparse(url)
    path = result.path
    vstr = VERSION_PATTERN.search(path)
    if not vstr:
        return result.scheme + "://" + result.netloc + "/" + filt.get_path()
    start, end = vstr.span()
    prefix = path[:start]
    version = '/' + filt.get_path(path[start + 1:end])
    postfix = path[end:].rstrip('/') if path[end:] else ''
    url = result.scheme + "://" + result.netloc + prefix + version + postfix
    return url


class Session(_session.Session):

    def __init__(self, profile, **kwargs):
        """Create a new Keystone auth session with a profile.

        :param profile: If the user has any special profiles such as the
            service name, region, version or interface, they may be provided
            in the profile object.  If no profiles are provided, the
            services that appear first in the service catalog will be used.
        :type profile: :class:`~openstack.profile.Profile`
        """
        super(Session, self).__init__(**kwargs)
        self.profile = profile

    def get_endpoint(self, auth=None, interface=None, **kwargs):
        """Override get endpoint to automate endpoint filering"""

        service_type = kwargs.get('service_type')
        filt = self.profile.get_filter(service_type)
        if filt.interface is None:
            filt.interface = interface
        url = super(Session, self).get_endpoint(auth, **filt.get_filter())
        return parse_url(filt, url)
