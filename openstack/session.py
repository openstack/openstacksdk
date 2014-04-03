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
Wrapper class for requests.Session adds some common OpenStack functionality

- log all requests and responses at debug level
- json-encode request body passed in to request() in json keyword arg
- set default user_agent at Session creation; set to None to skip the header
- set default verify at Session creation

"""

import json
import logging

import requests
from six.moves import urllib

import openstack


DEFAULT_USER_AGENT = 'python-OpenStackSDK/' + openstack.__version__

_logger = logging.getLogger(__name__)


class Session(requests.Session):

    _user_agent = DEFAULT_USER_AGENT

    def __init__(
            self,
            user_agent=None,
            verify=True,
    ):
        """Wraps requests.Session to add some OpenStack-specific features

        :param string user_agent: Set the default ``User-Agent`` header;
                                  Header is omitted if ``None`` and no value
                                  is supplied in the ``request()`` call.
        :param boolean/string verify: If ``True``, the SSL cert will be
                                      verified. A CA_BUNDLE path can also be
                                      provided.

        User agent handling is as follows:

        * if user_agent arg is included in the request() call, use it
        * else if 'User-Agent' is set in the headers dict, use it
        * else if user_agent arg is included in the __init__() call, use it
        * else use DEFAULT_USER_AGENT

        """

        super(Session, self).__init__()
        if user_agent:
            self._user_agent = user_agent
        self.verify = verify

    def request(self, method, url, **kwargs):
        """Send a request

        :param string method: Request HTTP method
        :param string url: Request URL

        The following additional kw args are supported:
        :param object json: Request body to be encoded as JSON
                            Overwrites ``data`` argument if present
        :param string user_agent: Set the ``User-Agent`` header; overwrites
                                  any value that may be in the headers dict.
                                  Header is omitted if ``None``.

        Remaining kw args from requests.Session.request() supported

        """

        headers = kwargs.setdefault('headers', {})

        # JSON-encode the data in json arg if present
        # Overwrites any existing 'data' value
        json_data = kwargs.pop('json', None)
        if json_data is not None:
            kwargs['data'] = json.dumps(json_data)
            headers['Content-Type'] = 'application/json'

        # Set User-Agent header if user_agent arg included, or
        # fall through the default chain as described above
        if 'user_agent' in kwargs:
            headers['User-Agent'] = kwargs.pop('user_agent')
        elif self._user_agent:
            headers.setdefault('User-Agent', self._user_agent)
        else:
            headers.setdefault('User-Agent', DEFAULT_USER_AGENT)

        self._log_request(method, url, **kwargs)

        resp = super(Session, self).request(method, url, **kwargs)

        self._log_response(resp)

        return resp

    def _log_request(self, method, url, **kwargs):
        if 'params' in kwargs and kwargs['params']:
            url += '?' + urllib.parse.urlencode(kwargs['params'])

        string_parts = [
            "curl -i",
            "-X '%s'" % method,
            "'%s'" % url,
        ]

        # kwargs overrides the default
        if (('verify' in kwargs and kwargs['verify'] is False) or
                not self.verify):
            string_parts.append('--insecure')

        for element in kwargs['headers'].items():
            header = " -H '%s: %s'" % element
            string_parts.append(header)

        _logger.debug("REQ: %s" % " ".join(string_parts))
        if 'data' in kwargs:
            _logger.debug("REQ BODY: %r\n" % (kwargs['data']))

    def _log_response(self, response):
        _logger.debug(
            "RESP: [%s] %r" % (
                response.status_code,
                response.headers,
            ),
        )
        if response._content_consumed:
            _logger.debug(
                "RESP BODY: %s",
                response.text,
            )
        _logger.debug(
            "encoding: %s",
            response.encoding,
        )
