import json
from operator import methodcaller

import requests

from urlobject import URLObject


class ServiceCatalog(object):
    def __init__(self, contents):
        self._contents = contents

    def find_endpoint_url(self, service_type, region):
        for service in self._contents:
            if service["type"] == service_type:
                for endpoint in service["endpoints"]:
                    if endpoint["region"] == region:
                        return URLObject(endpoint["publicURL"])
        raise ValueError


class KeystoneAuth(object):
    def __init__(self, identity_url, username, password):
        self._identity_url = URLObject(identity_url)
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._session.headers = {
            "content-type": "application/json",
            "accept": "application/json"
        }
        self._auth_token = None
        self._service_catalog = None

    def _perform_auth_request(self):
        auth_response = self._session.post(
            self._identity_url.add_path('tokens'),
            data=json.dumps({
                "auth": {
                    "passwordCredentials": {
                        "username": self._username,
                        "password": self._password
                    }
                },
                "tenantId": " "
            })
        )
        auth_response.raise_for_status()
        auth_body = auth_response.json()
        self._auth_token = auth_body["access"]["token"]["id"]
        self._service_catalog = ServiceCatalog(
            auth_body["access"]["serviceCatalog"]
        )

    def _handle_request_result(self, response, **kwargs):
        if response.status_code == 401:
            # We got an authentication failure, get a new token and try again.
            self._perform_auth_request()
            new_request = response.request.copy()
            new_request.headers["X-Auth-Token"] = self._auth_token
            new_response = response.connection.send(new_request, **kwargs)
            new_response.history.append(response)
            new_response.request = new_request
            return new_response
        else:
            return response

    def __call__(self, request):
        if self._auth_token is None:
            self._perform_auth_request()

        request.headers['X-Auth-Token'] = self._auth_token
        request.reigster_hook("response", self._handle_request_result)
        return request

    @property
    def service_catalog(self):
        if self._service_catalog is None:
            self._perform_auth_request()
        return self._service_catalog


class OpenStackClient(object):
    def __init__(self, auth, region):
        self._auth = auth
        self._region = region
        self._service_catalog = auth.service_catalog
        self._session = requests.Session()
        self._session.auth = auth
        self._session.headers = {
            "accept": "application/json"
        }

    @property
    def storage(self):
        return StorageClient(
            self._session, self._service_catalog, self._region
        )


class CreateContainerRequest(object):
    method = "PUT"
    body = ""

    def __init__(self, base_url, container_name):
        self._base_url = base_url
        self._container_name = container_name

    @property
    def url(self):
        return self._base_url.add_path(self._container_name)

    def parse_response(self, client, body):
        return Container(client, self._container_name)


class CreateObjectRequest(object):
    method = "PUT"

    def __init__(self, base_url, container_name, object_name, contents):
        self._base_url = base_url
        self._container_name = container_name
        self._object_name = object_name
        self._contents = contents

    @property
    def url(self):
        base = self._base_url
        return base.add_path(self._container_name).add_path(self._object_name)

    @property
    def body(self):
        return self._contents

    def parse_response(self, client, body):
        return Object(client, self._container_name, self._object_name)


class ListContainerObjectsRequest(object):
    method = "GET"
    body = ""

    def __init__(self, base_url, container_name):
        self._base_url = base_url
        self._container_name = container_name

    @property
    def url(self):
        return self._base_url.add_path(self._container_name)

    def parse_response(self, client, body):
        return [Object(client, self._container_name, o["name"]) for o in body]


class DeleteObjectRequest(object):
    method = "DELETE"
    body = ""

    def __init__(self, base_url, container_name, object_name):
        self._base_url = base_url
        self._container_name = container_name
        self._object_name = object_name

    @property
    def url(self):
        base = self._base_url
        return base.add_path(self._container_name).add_path(self._object_name)

    def parse_response(self, client, body):
        pass


class DeleteContainerRequest(object):
    method = "DELETE"
    body = ""

    def __init__(self, base_url, container_name):
        self._base_url = base_url
        self._container_name = container_name

    @property
    def url(self):
        return self._base_url.add_path(self._container_name)

    def parse_response(self, client, body):
        pass


class Container(object):
    def __init__(self, client, name):
        self._client = client
        self.name = name

    def create_object(self, name, contents):
        return self._client.create_object(self.name, name, contents)

    def list_objects(self):
        return self._client.list_objects(self.name)

    def delete(self):
        self._client.delete_container(self.name)


class Object(object):
    def __init__(self, client, container_name, object_name):
        self._client = client
        self.container_name = container_name
        self.object_name = object_name

    def __repr__(self):
        return "<Object(%s, %s)>" % (self.container_name, self.object_name)

    def delete(self):
        self._client.delete_object(self.container_name, self.object_name)


class StorageClient(object):
    def __init__(self, session, service_catalog, region):
        self._session = session
        self._base_url = service_catalog.find_endpoint_url(
            "object-store", region
        )

    def _create_api_caller(request_cls, body_handler=lambda response: None):
        def inner(self, *args, **kwargs):
            request = request_cls(self._base_url, *args, **kwargs)
            response = self._session.request(
                request.method, request.url, data=request.body
            )
            response.raise_for_status()
            return request.parse_response(self, body_handler(response))
        return inner

    create_container = _create_api_caller(CreateContainerRequest)
    create_object = _create_api_caller(CreateObjectRequest)
    list_objects = _create_api_caller(
        ListContainerObjectsRequest, methodcaller("json")
    )
    delete_object = _create_api_caller(DeleteObjectRequest)
    delete_container = _create_api_caller(DeleteContainerRequest)


if __name__ == "__main__":
    client = OpenStackClient(
        KeystoneAuth(
            "https://identity.api.rackspacecloud.com/v2.0/",
            "username",
            "password",
        ),
        region="IAD"
    )
    container = client.storage.create_container("boom")
    container.create_object("bar", contents="lolwut")
    objs = container.list_objects()
    print objs
    [obj] = objs
    obj.delete()
    container.delete()
