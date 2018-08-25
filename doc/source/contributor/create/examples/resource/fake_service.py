# Apache 2 header omitted for brevity

from openstack import service_description
from openstack.fake.v2 import _proxy as _proxy_v2


class FakeService(service_description.ServiceDescription):
    """The fake service."""

    supported_versions = {
        '2': _proxy_v2.Proxy,
    }
