# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import sys

import munch
from requests import exceptions as _rex

from shade import _log


class OpenStackCloudException(Exception):

    log_inner_exceptions = False

    def __init__(self, message, extra_data=None, **kwargs):
        args = [message]
        if extra_data:
            if isinstance(extra_data, munch.Munch):
                extra_data = extra_data.toDict()
            args.append("Extra: {0}".format(str(extra_data)))
        super(OpenStackCloudException, self).__init__(*args, **kwargs)
        self.extra_data = extra_data
        self.inner_exception = sys.exc_info()
        self.orig_message = message

    def log_error(self, logger=None):
        if not logger:
            logger = _log.setup_logging('shade.exc')
        if self.inner_exception and self.inner_exception[1]:
            logger.error(self.orig_message, exc_info=self.inner_exception)

    def __str__(self):
        message = Exception.__str__(self)
        if (self.inner_exception and self.inner_exception[1]
                and not self.orig_message.endswith(
                    str(self.inner_exception[1]))):
            message = "%s (Inner Exception: %s)" % (
                message,
                str(self.inner_exception[1]))
        if self.log_inner_exceptions:
            self.log_error()
        return message


class OpenStackCloudTimeout(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableExtension(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableFeature(OpenStackCloudException):
    pass


class OpenStackCloudHTTPError(OpenStackCloudException, _rex.HTTPError):

    def __init__(self, *args, **kwargs):
        OpenStackCloudException.__init__(self, *args, **kwargs)
        _rex.HTTPError.__init__(self, *args, **kwargs)


class OpenStackCloudBadRequest(OpenStackCloudHTTPError):
    """There is something wrong with the request payload.

    Possible reasons can include malformed json or invalid values to parameters
    such as flavorRef to a server create.
    """


class OpenStackCloudURINotFound(OpenStackCloudHTTPError):
    pass

# Backwards compat
OpenStackCloudResourceNotFound = OpenStackCloudURINotFound


def _log_response_extras(response):
    # Sometimes we get weird HTML errors. This is usually from load balancers
    # or other things. Log them to a special logger so that they can be
    # toggled indepdently - and at debug level so that a person logging
    # shade.* only gets them at debug.
    if response.headers.get('content-type') != 'text/html':
        return
    try:
        if int(response.headers.get('content-length', 0)) == 0:
            return
    except Exception:
        return
    logger = _log.setup_logging('shade.http')
    if response.reason:
        logger.debug(
            "Non-standard error '{reason}' returned from {url}:".format(
                reason=response.reason,
                url=response.url))
    else:
        logger.debug(
            "Non-standard error returned from {url}:".format(
                url=response.url))
    for response_line in response.text.split('\n'):
        logger.debug(response_line)


# Logic shamelessly stolen from requests
def raise_from_response(response, error_message=None):
    msg = ''
    if 400 <= response.status_code < 500:
        source = "Client"
    elif 500 <= response.status_code < 600:
        source = "Server"
    else:
        return

    remote_error = "Error for url: {url}".format(url=response.url)
    try:
        details = response.json()
        # Nova returns documents that look like
        # {statusname: 'message': message, 'code': code}
        detail_keys = list(details.keys())
        if len(detail_keys) == 1:
            detail_key = detail_keys[0]
            detail_message = details[detail_key].get('message')
            if detail_message:
                remote_error += " {message}".format(message=detail_message)
    except ValueError:
        if response.reason:
            remote_error += " {reason}".format(reason=response.reason)

    _log_response_extras(response)

    if error_message:
        msg = '{error_message}. ({code}) {source} {remote_error}'.format(
            error_message=error_message,
            source=source,
            code=response.status_code,
            remote_error=remote_error)
    else:
        msg = '({code}) {source} {remote_error}'.format(
            code=response.status_code,
            source=source,
            remote_error=remote_error)

    # Special case 404 since we raised a specific one for neutron exceptions
    # before
    if response.status_code == 404:
        raise OpenStackCloudURINotFound(msg, response=response)
    elif response.status_code == 400:
        raise OpenStackCloudBadRequest(msg, response=response)
    if msg:
        raise OpenStackCloudHTTPError(msg, response=response)
