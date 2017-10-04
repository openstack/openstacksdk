# Apache 2 header omitted for brevity

from openstack import service_filter


class FakeService(service_filter.ServiceFilter):
    """The fake service."""

    valid_versions = [service_filter.ValidVersion('v2')]

    def __init__(self, version=None):
        """Create a fake service."""
        super(FakeService, self).__init__(service_type='fake', version=version)
