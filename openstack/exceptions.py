# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Exception definitions.
"""

import re

from requests import exceptions as _rex
import six


class SDKException(Exception):
    """The base exception class for all exceptions this library raises."""
    def __init__(self, message=None, extra_data=None):
        self.message = self.__class__.__name__ if message is None else message
        self.extra_data = extra_data
        super(SDKException, self).__init__(self.message)
OpenStackCloudException = SDKException


class EndpointNotFound(SDKException):
    """A mismatch occurred between what the client and server expect."""
    def __init__(self, message=None):
        super(EndpointNotFound, self).__init__(message)


class InvalidResponse(SDKException):
    """The response from the server is not valid for this request."""

    def __init__(self, response):
        super(InvalidResponse, self).__init__()
        self.response = response


class InvalidRequest(SDKException):
    """The request to the server is not valid."""

    def __init__(self, message=None):
        super(InvalidRequest, self).__init__(message)


class HttpException(SDKException, _rex.HTTPError):

    def __init__(self, message='Error', response=None,
                 http_status=None,
                 details=None, request_id=None):
        # TODO(shade) Remove http_status parameter and the ability for response
        # to be None once we're not mocking Session everywhere.
        if not message:
            if response:
                message = "{name}: {code}".format(
                    name=self.__class__.__name__,
                    code=response.status_code)
            else:
                message = "{name}: Unknown error".format(
                    name=self.__class__.__name__)

        # Call directly rather than via super to control parameters
        SDKException.__init__(self, message=message)
        _rex.HTTPError.__init__(self, message, response=response)

        if response:
            self.request_id = response.headers.get('x-openstack-request-id')
            self.status_code = response.status_code
        else:
            self.request_id = request_id
            self.status_code = http_status
        self.details = details
        self.url = self.request and self.request.url or None
        self.method = self.request and self.request.method or None
        self.source = "Server"
        if self.status_code is not None and (400 <= self.status_code < 500):
            self.source = "Client"

    def __unicode__(self):
        # 'Error' is the default value for self.message. If self.message isn't
        # 'Error', then someone has set a more informative error message
        # and we should use it. If it is 'Error', then we should construct a
        # better message from the information we do have.
        if not self.url or self.message != 'Error':
            return super(HttpException, self).__str__()
        if self.url:
            remote_error = "{source} Error for url: {url}".format(
                source=self.source, url=self.url)
            if self.details:
                remote_error += ', '
        if self.details:
            remote_error += six.text_type(self.details)

        return "{message}: {remote_error}".format(
            message=super(HttpException, self).__str__(),
            remote_error=remote_error)

    def __str__(self):
        return self.__unicode__()


class NotFoundException(HttpException):
    """HTTP 404 Not Found."""
    pass


class BadRequestException(HttpException):
    """HTTP 400 Bad Request."""
    pass


class MethodNotSupported(SDKException):
    """The resource does not support this operation type."""
    def __init__(self, resource, method):
        # This needs to work with both classes and instances.
        try:
            name = resource.__name__
        except AttributeError:
            name = resource.__class__.__name__

        message = ('The %s method is not supported for %s.%s' %
                   (method, resource.__module__, name))
        super(MethodNotSupported, self).__init__(message=message)


class DuplicateResource(SDKException):
    """More than one resource exists with that name."""
    pass


class ResourceNotFound(NotFoundException):
    """No resource exists with that name or id."""
    pass


class ResourceTimeout(SDKException):
    """Timeout waiting for resource."""
    pass


class ResourceFailure(SDKException):
    """General resource failure."""
    pass


class InvalidResourceQuery(SDKException):
    """Invalid query params for resource."""
    pass


def raise_from_response(response, error_message=None):
    """Raise an instance of an HTTPException based on keystoneauth response."""
    if response.status_code < 400:
        return

    if response.status_code == 404:
        cls = NotFoundException
    elif response.status_code == 400:
        cls = BadRequestException
    else:
        cls = HttpException

    details = None
    content_type = response.headers.get('content-type', '')
    if response.content and 'application/json' in content_type:
        # Iterate over the nested objects to retrieve "message" attribute.
        # TODO(shade) Add exception handling for times when the content type
        # is lying.

        try:
            content = response.json()
            messages = [obj.get('message') for obj in content.values()
                        if isinstance(obj, dict)]
            # Join all of the messages together nicely and filter out any
            # objects that don't have a "message" attr.
            details = '\n'.join(msg for msg in messages if msg)
        except Exception:
            details = response.text
    elif response.content and 'text/html' in content_type:
        # Split the lines, strip whitespace and inline HTML from the response.
        details = [re.sub(r'<.+?>', '', i.strip())
                   for i in response.text.splitlines()]
        details = list(set([msg for msg in details if msg]))
        # Return joined string separated by colons.
        details = ': '.join(details)
    if not details and response.reason:
        details = response.reason
    else:
        details = response.text

    http_status = response.status_code
    request_id = response.headers.get('x-openstack-request-id')

    raise cls(
        message=error_message, response=response, details=details,
        http_status=http_status, request_id=request_id
    )


class ArgumentDeprecationWarning(Warning):
    """A deprecated argument has been provided."""
    pass


class ConfigException(SDKException):
    """Something went wrong with parsing your OpenStack Config."""
