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
# under the License.V

"""
fakes
----------------------------------

Fakes used for testing
"""


PROJECT_ID = '1c36b64c840a42cd9e9b931a369337f0'
FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8dddd'
CHOCOLATE_FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8ddde'
STRAWBERRY_FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8dddf'
COMPUTE_ENDPOINT = 'https://compute.example.com/v2.1/{project_id}'.format(
    project_id=PROJECT_ID)


def make_fake_flavor(flavor_id, name, ram=100, disk=1600, vcpus=24):
    return {
        u'OS-FLV-DISABLED:disabled': False,
        u'OS-FLV-EXT-DATA:ephemeral': 0,
        u'disk': disk,
        u'id': flavor_id,
        u'links': [{
            u'href': u'{endpoint}/flavors/{id}'.format(
                endpoint=COMPUTE_ENDPOINT, id=flavor_id),
            u'rel': u'self'
        }, {
            u'href': u'{endpoint}/flavors/{id}'.format(
                endpoint=COMPUTE_ENDPOINT, id=flavor_id),
            u'rel': u'bookmark'
        }],
        u'name': name,
        u'os-flavor-access:is_public': True,
        u'ram': ram,
        u'rxtx_factor': 1.0,
        u'swap': u'',
        u'vcpus': vcpus
    }
FAKE_FLAVOR = make_fake_flavor(FLAVOR_ID, 'vanilla')
FAKE_CHOCOLATE_FLAVOR = make_fake_flavor(
    CHOCOLATE_FLAVOR_ID, 'chocolate', ram=200)
FAKE_STRAWBERRY_FLAVOR = make_fake_flavor(
    STRAWBERRY_FLAVOR_ID, 'strawberry', ram=300)
FAKE_FLAVOR_LIST = [FAKE_FLAVOR, FAKE_CHOCOLATE_FLAVOR, FAKE_STRAWBERRY_FLAVOR]


class FakeEndpoint(object):
    def __init__(self, id, service_id, region, publicurl, internalurl=None,
                 adminurl=None):
        self.id = id
        self.service_id = service_id
        self.region = region
        self.publicurl = publicurl
        self.internalurl = internalurl
        self.adminurl = adminurl


class FakeEndpointv3(object):
    def __init__(self, id, service_id, region, url, interface=None):
        self.id = id
        self.service_id = service_id
        self.region = region
        self.url = url
        self.interface = interface


class FakeFlavor(object):
    def __init__(self, id, name, ram, extra_specs=None):
        self.id = id
        self.name = name
        self.ram = ram
        # Leave it unset if we don't pass it in to test that normalize_ works
        # but we also have to be able to pass one in to deal with mocks
        if extra_specs:
            self.extra_specs = extra_specs

    def get_keys(self):
        return {}


class FakeFloatingIP(object):
    def __init__(self, id, pool, ip, fixed_ip, instance_id):
        self.id = id
        self.pool = pool
        self.ip = ip
        self.fixed_ip = fixed_ip
        self.instance_id = instance_id


class FakeFloatingIPPool(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class FakeProject(object):
    def __init__(self, id, domain_id=None):
        self.id = id
        self.domain_id = domain_id or 'default'


class FakeServer(object):
    def __init__(
            self, id, name, status, addresses=None,
            accessIPv4='', accessIPv6='', private_v4='',
            private_v6='', public_v4='', public_v6='',
            interface_ip='',
            flavor=None, image=None, adminPass=None,
            metadata=None):
        self.id = id
        self.name = name
        self.status = status
        if not addresses:
            self.addresses = {}
        else:
            self.addresses = addresses
        if not flavor:
            flavor = {}
        self.flavor = flavor
        if not image:
            image = {}
        self.image = image
        self.accessIPv4 = accessIPv4
        self.accessIPv6 = accessIPv6
        self.private_v4 = private_v4
        self.public_v4 = public_v4
        self.private_v6 = private_v6
        self.public_v6 = public_v6
        self.adminPass = adminPass
        self.metadata = metadata
        self.interface_ip = interface_ip


class FakeServerGroup(object):
    def __init__(self, id, name, policies):
        self.id = id
        self.name = name
        self.policies = policies


class FakeService(object):
    def __init__(self, id, name, type, service_type, description='',
                 enabled=True):
        self.id = id
        self.name = name
        self.type = type
        self.service_type = service_type
        self.description = description
        self.enabled = enabled


class FakeUser(object):
    def __init__(self, id, email, name, domain_id=None, description=None):
        self.id = id
        self.email = email
        self.name = name
        self.description = description
        if domain_id is not None:
            self.domain_id = domain_id


class FakeVolume(object):
    def __init__(
            self, id, status, name, attachments=[],
            size=75):
        self.id = id
        self.status = status
        self.name = name
        self.attachments = attachments
        self.size = size
        self.snapshot_id = 'id:snapshot'
        self.description = 'description'
        self.volume_type = 'type:volume'
        self.availability_zone = 'az1'
        self.created_at = '1900-01-01 12:34:56'
        self.source_volid = '12345'
        self.metadata = {}


class FakeVolumeSnapshot(object):
    def __init__(
            self, id, status, name, description, size=75):
        self.id = id
        self.status = status
        self.name = name
        self.description = description
        self.size = size
        self.created_at = '1900-01-01 12:34:56'
        self.volume_id = '12345'
        self.metadata = {}


class FakeMachine(object):
    def __init__(self, id, name=None, driver=None, driver_info=None,
                 chassis_uuid=None, instance_info=None, instance_uuid=None,
                 properties=None):
        self.id = id
        self.name = name
        self.driver = driver
        self.driver_info = driver_info
        self.chassis_uuid = chassis_uuid
        self.instance_info = instance_info
        self.instance_uuid = instance_uuid
        self.properties = properties


class FakeMachinePort(object):
    def __init__(self, id, address, node_id):
        self.id = id
        self.address = address
        self.node_id = node_id


class FakeSecgroup(object):
    def __init__(self, id, name, description='', rules=None):
        self.id = id
        self.name = name
        self.description = description
        self.rules = rules


class FakeNovaSecgroupRule(object):
    def __init__(self, id, from_port=None, to_port=None, ip_protocol=None,
                 cidr=None, parent_group_id=None):
        self.id = id
        self.from_port = from_port
        self.to_port = to_port
        self.ip_protocol = ip_protocol
        if cidr:
            self.ip_range = {'cidr': cidr}
        self.parent_group_id = parent_group_id


class FakeKeypair(object):
    def __init__(self, id, name, public_key):
        self.id = id
        self.name = name
        self.public_key = public_key


class FakeDomain(object):
    def __init__(self, id, name, description, enabled):
        self.id = id
        self.name = name
        self.description = description
        self.enabled = enabled


class FakeRole(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class FakeGroup(object):
    def __init__(self, id, name, description, domain_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.domain_id = domain_id or 'default'


class FakeHypervisor(object):
    def __init__(self, id, hostname):
        self.id = id
        self.hypervisor_hostname = hostname


class FakeStack(object):
    def __init__(self, id, name, description=None, status='CREATE_COMPLETE'):
        self.id = id
        self.name = name
        self.stack_name = name
        self.stack_description = description
        self.stack_status = status


class FakeZone(object):
    def __init__(self, id, name, type_, email, description,
                 ttl, masters):
        self.id = id
        self.name = name
        self.type_ = type_
        self.email = email
        self.description = description
        self.ttl = ttl
        self.masters = masters


class FakeRecordset(object):
    def __init__(self, zone, id, name, type_, description,
                 ttl, records):
        self.zone = zone
        self.id = id
        self.name = name
        self.type_ = type_
        self.description = description
        self.ttl = ttl
        self.records = records


class FakeAggregate(object):
    def __init__(self, id, name, availability_zone=None, metadata=None,
                 hosts=None):
        self.id = id
        self.name = name
        self.availability_zone = availability_zone
        if not metadata:
            metadata = {}
        self.metadata = metadata
        if not hosts:
            hosts = []
        self.hosts = hosts
