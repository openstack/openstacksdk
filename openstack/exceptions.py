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

import json
import re
import typing as ty
import warnings

import requests
from requests import exceptions as _rex

from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    from openstack import resource


class SDKException(Exception):
    """The base exception class for all exceptions this library raises."""

    def __init__(
        self, message: ty.Optional[str] = None, extra_data: ty.Any = None
    ):
        self.message = self.__class__.__name__ if message is None else message
        self.extra_data = extra_data
        super().__init__(self.message)


class EndpointNotFound(SDKException):
    """A mismatch occurred between what the client and server expect."""

    def __init__(self, message: ty.Optional[str] = None):
        super().__init__(message)


class InvalidResponse(SDKException):
    """The response from the server is not valid for this request."""

    def __init__(self, message: ty.Optional[str] = None):
        super().__init__(message)


class InvalidRequest(SDKException):
    """The request to the server is not valid."""

    def __init__(self, message: ty.Optional[str] = None):
        super().__init__(message)


class HttpException(SDKException, _rex.HTTPError):
    """The base exception for all HTTP error responses."""

    source: str
    status_code: ty.Optional[int]

    def __init__(
        self,
        message: ty.Optional[str] = 'Error',
        response: ty.Optional[requests.Response] = None,
        http_status: ty.Optional[int] = None,
        details: ty.Optional[str] = None,
        request_id: ty.Optional[str] = None,
    ):
        if http_status is not None:
            warnings.warn(
                "The 'http_status' parameter is unnecessary and will be "
                "removed in a future release",
                os_warnings.RemovedInSDK50Warning,
            )

        if request_id is not None:
            warnings.warn(
                "The 'request_id' parameter is unnecessary and will be "
                "removed in a future release",
                os_warnings.RemovedInSDK50Warning,
            )

        if not message:
            if response is not None:
                message = f"{self.__class__.__name__}: {response.status_code}"
            else:
                message = f"{self.__class__.__name__}: Unknown error"
            status = (
                response.status_code
                if response is not None
                else 'Unknown error'
            )
            message = f'{self.__class__.__name__}: {status}'

        # Call directly rather than via super to control parameters
        SDKException.__init__(self, message=message)
        _rex.HTTPError.__init__(self, message, response=response)

        if response is not None:
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

    def __str__(self) -> str:
        # 'Error' is the default value for self.message. If self.message isn't
        # 'Error', then someone has set a more informative error message
        # and we should use it. If it is 'Error', then we should construct a
        # better message from the information we do have.
        if not self.url or self.message == 'Error':
            return self.message
        if self.url:
            remote_error = f"{self.source} Error for url: {self.url}"
            if self.details:
                remote_error += ', '
        if self.details:
            remote_error += str(self.details)

        return f"{super().__str__()}: {remote_error}"


class BadRequestException(HttpException):
    """HTTP 400 Bad Request."""


class NotFoundException(HttpException):
    """HTTP 404 Not Found."""


class ForbiddenException(HttpException):
    """HTTP 403 Forbidden Request."""


class ConflictException(HttpException):
    """HTTP 409 Conflict."""


class PreconditionFailedException(HttpException):
    """HTTP 412 Precondition Failed."""


class MethodNotSupported(SDKException):
    """The resource does not support this operation type."""

    def __init__(
        self,
        resource: ty.Union['resource.Resource', type['resource.Resource']],
        method: str,
    ):
        # This needs to work with both classes and instances.
        try:
            name = resource.__name__
        except AttributeError:
            name = resource.__class__.__name__

        message = f'The {method} method is not supported for {resource.__module__}.{name}'
        super().__init__(message=message)


class DuplicateResource(SDKException):
    """More than one resource exists with that name."""


class ResourceTimeout(SDKException):
    """Timeout waiting for resource."""


class ResourceFailure(SDKException):
    """General resource failure."""


class InvalidResourceQuery(SDKException):
    """Invalid query params for resource."""


def _extract_message(obj: ty.Any) -> ty.Optional[str]:
    if isinstance(obj, dict):
        # Most of services: compute, network
        if obj.get('message'):
            return str(obj['message'])
        # Ironic starting with Stein
        elif obj.get('faultstring'):
            return str(obj['faultstring'])
    elif isinstance(obj, str):
        # Ironic before Stein has double JSON encoding, nobody remembers why.
        try:
            obj = json.loads(obj)
        except Exception:  # noqa: S110
            # This is best effort. Ignore any errors.
            pass
        else:
            return _extract_message(obj)
    return None


def raise_from_response(
    response: requests.Response,
    error_message: ty.Optional[str] = None,
) -> None:
    """Raise an instance of an HTTPException based on keystoneauth response."""
    if response.status_code < 400:
        return

    cls: type[SDKException]
    if response.status_code == 400:
        cls = BadRequestException
    elif response.status_code == 403:
        cls = ForbiddenException
    elif response.status_code == 404:
        cls = NotFoundException
    elif response.status_code == 409:
        cls = ConflictException
    elif response.status_code == 412:
        cls = PreconditionFailedException
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
            messages = [_extract_message(obj) for obj in content.values()]
            if not any(messages):
                # Exception dict may be the root dict in projects that use WSME
                messages = [_extract_message(content)]
            # Join all of the messages together nicely and filter out any
            # objects that don't have a "message" attr.
            details = '\n'.join(msg for msg in messages if msg)
        except Exception:
            details = response.text
    elif response.content and 'text/html' in content_type:
        messages = []
        for line in response.text.splitlines():
            message = re.sub(r'<.+?>', '', line.strip())
            if message not in messages:
                messages.append(message)

        # Return joined string separated by colons.
        details = ': '.join(msg for msg in messages if msg)

    if not details:
        details = response.reason if response.reason else response.text

    raise cls(
        message=error_message,
        response=response,
        details=details,
    )


class ConfigException(SDKException):
    """Something went wrong with parsing your OpenStack Config."""


class NotSupported(SDKException):
    """Request cannot be performed by any supported API version."""


class ValidationException(SDKException):
    """Validation failed for resource."""


class ServiceDisabledException(ConfigException):
    """This service is disabled for reasons."""


class ServiceDiscoveryException(SDKException):
    """The service cannot be discovered."""


# Backwards compatibility
OpenStackCloudException = SDKException
ResourceNotFound = NotFoundException
