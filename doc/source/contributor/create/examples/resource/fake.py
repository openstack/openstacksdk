# Apache 2 header omitted for brevity

from openstack.fake import fake_service
from openstack import resource


class Fake(resource.Resource):
    resource_key = "resource"
    resources_key = "resources"
    base_path = "/fake"
    service = fake_service.FakeService()

    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The name of this resource.
    name = resource.Body("name", alternate_id=True)
    #: The value of the resource. Also available in headers.
    value = resource.Body("value", alias="x-resource-value")
    #: Is this resource cool? If so, set it to True.
    #: This is a multi-line comment about cool stuff.
    cool = resource.Body("cool", type=bool)
