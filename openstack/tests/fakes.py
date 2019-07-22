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

import datetime
import json
import hashlib
import uuid

from openstack.orchestration.util import template_format
from openstack.cloud import meta

PROJECT_ID = '1c36b64c840a42cd9e9b931a369337f0'
FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8dddd'
CHOCOLATE_FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8ddde'
STRAWBERRY_FLAVOR_ID = u'0c1d9008-f546-4608-9e8f-f8bdaec8dddf'
COMPUTE_ENDPOINT = 'https://compute.example.com/v2.1'
ORCHESTRATION_ENDPOINT = 'https://orchestration.example.com/v1/{p}'.format(
    p=PROJECT_ID)
NO_MD5 = '93b885adfe0da089cdf634904fd59f71'
NO_SHA256 = '6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d'
FAKE_PUBLIC_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkF3MX59OrlBs3dH5CU7lNmvpbrgZxSpyGj"
    "lnE8Flkirnc/Up22lpjznoxqeoTAwTW034k7Dz6aYIrZGmQwe2TkE084yqvlj45Dkyoj95fW/"
    "sZacm0cZNuL69EObEGHdprfGJQajrpz22NQoCD8TFB8Wv+8om9NH9Le6s+WPe98WC77KLw8qg"
    "fQsbIey+JawPWl4O67ZdL5xrypuRjfIPWjgy/VH85IXg/Z/GONZ2nxHgSShMkwqSFECAC5L3P"
    "HB+0+/12M/iikdatFSVGjpuHvkLOs3oe7m6HlOfluSJ85BzLWBbvva93qkGmLg4ZAc8rPh2O+"
    "YIsBUHNLLMM/oQp Generated-by-Nova\n")


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
FAKE_TEMPLATE = '''heat_template_version: 2014-10-16

parameters:
  length:
    type: number
    default: 10

resources:
  my_rand:
    type: OS::Heat::RandomString
    properties:
      length: {get_param: length}
outputs:
  rand:
    value:
      get_attr: [my_rand, value]
'''
FAKE_TEMPLATE_CONTENT = template_format.parse(FAKE_TEMPLATE)


def make_fake_server(
        server_id, name, status='ACTIVE', admin_pass=None,
        addresses=None, image=None, flavor=None):
    if addresses is None:
        if status == 'ACTIVE':
            addresses = {
                "private": [
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 6,
                        "addr": "fddb:b018:307:0:f816:3eff:fedf:b08d",
                        "OS-EXT-IPS:type": "fixed"},
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 4,
                        "addr": "10.1.0.9",
                        "OS-EXT-IPS:type": "fixed"},
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 4,
                        "addr": "172.24.5.5",
                        "OS-EXT-IPS:type": "floating"}]}
        else:
            addresses = {}
    if image is None:
        image = {"id": "217f3ab1-03e0-4450-bf27-63d52b421e9e",
                 "links": []}
    if flavor is None:
        flavor = {"id": "64",
                  "links": []}

    server = {
        "OS-EXT-STS:task_state": None,
        "addresses": addresses,
        "links": [],
        "image": image,
        "OS-EXT-STS:vm_state": "active",
        "OS-SRV-USG:launched_at": "2017-03-23T23:57:38.000000",
        "flavor": flavor,
        "id": server_id,
        "security_groups": [{"name": "default"}],
        "user_id": "9c119f4beaaa438792ce89387362b3ad",
        "OS-DCF:diskConfig": "MANUAL",
        "accessIPv4": "",
        "accessIPv6": "",
        "progress": 0,
        "OS-EXT-STS:power_state": 1,
        "OS-EXT-AZ:availability_zone": "nova",
        "metadata": {},
        "status": status,
        "updated": "2017-03-23T23:57:39Z",
        "hostId": "89d165f04384e3ffa4b6536669eb49104d30d6ca832bba2684605dbc",
        "OS-SRV-USG:terminated_at": None,
        "key_name": None,
        "name": name,
        "created": "2017-03-23T23:57:12Z",
        "tenant_id": PROJECT_ID,
        "os-extended-volumes:volumes_attached": [],
        "config_drive": "True"}
    if admin_pass:
        server['adminPass'] = admin_pass
    return json.loads(json.dumps(server))


def make_fake_keypair(name):
    # Note: this is literally taken from:
    # https://docs.openstack.org/api-ref/compute/
    return {
        "fingerprint": "7e:eb:ab:24:ba:d1:e1:88:ae:9a:fb:66:53:df:d3:bd",
        "name": name,
        "type": "ssh",
        "public_key": FAKE_PUBLIC_KEY,
        "created_at": datetime.datetime.now().isoformat(),
    }


def make_fake_stack(id, name, description=None, status='CREATE_COMPLETE'):
    return {
        'creation_time': '2017-03-23T23:57:12Z',
        'deletion_time': '2017-03-23T23:57:12Z',
        'description': description,
        'id': id,
        'links': [],
        'parent': None,
        'stack_name': name,
        'stack_owner': None,
        'stack_status': status,
        'stack_user_project_id': PROJECT_ID,
        'tags': None,
        'updated_time': '2017-03-23T23:57:12Z',
    }


def make_fake_stack_event(
        id, name, status='CREATE_COMPLETED', resource_name='id'):
    event_id = uuid.uuid4().hex
    self_url = "{endpoint}/stacks/{name}/{id}/resources/{name}/events/{event}"
    resource_url = "{endpoint}/stacks/{name}/{id}/resources/{name}"
    return {
        "resource_name": id if resource_name == 'id' else name,
        "event_time": "2017-03-26T19:38:18",
        "links": [
            {
                "href": self_url.format(
                    endpoint=ORCHESTRATION_ENDPOINT,
                    name=name, id=id, event=event_id),
                "rel": "self"
            }, {
                "href": resource_url.format(
                    endpoint=ORCHESTRATION_ENDPOINT,
                    name=name, id=id),
                "rel": "resource"
            }, {
                "href": "{endpoint}/stacks/{name}/{id}".format(
                    endpoint=ORCHESTRATION_ENDPOINT,
                    name=name, id=id),
                "rel": "stack"
            }],
        "logical_resource_id": name,
        "resource_status": status,
        "resource_status_reason": "",
        "physical_resource_id": id,
        "id": event_id,
    }


def make_fake_image(
        image_id=None, md5=NO_MD5, sha256=NO_SHA256, status='active',
        image_name=u'fake_image',
        data=None,
        checksum=u'ee36e35a297980dee1b514de9803ec6d'):
    if data:
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(data, 'rb') as file_obj:
            for chunk in iter(lambda: file_obj.read(8192), b''):
                md5.update(chunk)
                sha256.update(chunk)
        md5 = md5.hexdigest()
        sha256 = sha256.hexdigest()
    return {
        u'image_state': u'available',
        u'container_format': u'bare',
        u'min_ram': 0,
        u'ramdisk_id': 'fake_ramdisk_id',
        u'updated_at': u'2016-02-10T05:05:02Z',
        u'file': '/v2/images/' + image_id + '/file',
        u'size': 3402170368,
        u'image_type': u'snapshot',
        u'disk_format': u'qcow2',
        u'id': image_id,
        u'schema': u'/v2/schemas/image',
        u'status': status,
        u'tags': [],
        u'visibility': u'private',
        u'locations': [{
            u'url': u'http://127.0.0.1/images/' + image_id,
            u'metadata': {}}],
        u'min_disk': 40,
        u'virtual_size': None,
        u'name': image_name,
        u'checksum': md5 or checksum,
        u'created_at': u'2016-02-10T05:03:11Z',
        u'owner_specified.openstack.md5': md5 or NO_MD5,
        u'owner_specified.openstack.sha256': sha256 or NO_SHA256,
        u'owner_specified.openstack.object': 'images/{name}'.format(
            name=image_name),
        u'protected': False}


def make_fake_machine(machine_name, machine_id=None):
    if not machine_id:
        machine_id = uuid.uuid4().hex
    return meta.obj_to_munch(FakeMachine(
        id=machine_id,
        name=machine_name))


def make_fake_port(address, node_id=None, port_id=None):
    if not node_id:
        node_id = uuid.uuid4().hex
    if not port_id:
        port_id = uuid.uuid4().hex
    return meta.obj_to_munch(FakeMachinePort(
        id=port_id,
        address=address,
        node_id=node_id))


class FakeFloatingIP(object):
    def __init__(self, id, pool, ip, fixed_ip, instance_id):
        self.id = id
        self.pool = pool
        self.ip = ip
        self.fixed_ip = fixed_ip
        self.instance_id = instance_id


def make_fake_server_group(id, name, policies):
    return json.loads(json.dumps({
        'id': id,
        'name': name,
        'policies': policies,
        'members': [],
        'metadata': {},
    }))


def make_fake_hypervisor(id, name):
    return json.loads(json.dumps({
        'id': id,
        'hypervisor_hostname': name,
        'state': 'up',
        'status': 'enabled',
        "cpu_info": {
            "arch": "x86_64",
            "model": "Nehalem",
            "vendor": "Intel",
            "features": [
                "pge",
                "clflush"
            ],
            "topology": {
                "cores": 1,
                "threads": 1,
                "sockets": 4
            }
        },
        "current_workload": 0,
        "status": "enabled",
        "state": "up",
        "disk_available_least": 0,
        "host_ip": "1.1.1.1",
        "free_disk_gb": 1028,
        "free_ram_mb": 7680,
        "hypervisor_type": "fake",
        "hypervisor_version": 1000,
        "local_gb": 1028,
        "local_gb_used": 0,
        "memory_mb": 8192,
        "memory_mb_used": 512,
        "running_vms": 0,
        "service": {
            "host": "host1",
            "id": 7,
            "disabled_reason": None
        },
        "vcpus": 1,
        "vcpus_used": 0
    }))


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
                 properties=None, reservation=None, last_error=None,
                 provision_state='available'):
        self.uuid = id
        self.name = name
        self.driver = driver
        self.driver_info = driver_info
        self.chassis_uuid = chassis_uuid
        self.instance_info = instance_info
        self.instance_uuid = instance_uuid
        self.properties = properties
        self.reservation = reservation
        self.last_error = last_error
        self.provision_state = provision_state


class FakeMachinePort(object):
    def __init__(self, id, address, node_id):
        self.uuid = id
        self.address = address
        self.node_uuid = node_id


def make_fake_neutron_security_group(
        id, name, description, rules, project_id=None):
    if not rules:
        rules = []
    if not project_id:
        project_id = PROJECT_ID
    return json.loads(json.dumps({
        'id': id,
        'name': name,
        'description': description,
        'project_id': project_id,
        'tenant_id': project_id,
        'security_group_rules': rules,
    }))


def make_fake_nova_security_group_rule(
        id, from_port, to_port, ip_protocol, cidr):
    return json.loads(json.dumps({
        'id': id,
        'from_port': int(from_port),
        'to_port': int(to_port),
        'ip_protcol': 'tcp',
        'ip_range': {
            'cidr': cidr
        }
    }))


def make_fake_nova_security_group(id, name, description, rules):
    if not rules:
        rules = []
    return json.loads(json.dumps({
        'id': id,
        'name': name,
        'description': description,
        'tenant_id': PROJECT_ID,
        'rules': rules,
    }))


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


class FakeHypervisor(object):
    def __init__(self, id, hostname):
        self.id = id
        self.hypervisor_hostname = hostname


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


def make_fake_aggregate(id, name, availability_zone='nova',
                        metadata=None, hosts=None):
    if not metadata:
        metadata = {}
    if not hosts:
        hosts = []
    return json.loads(json.dumps({
        "availability_zone": availability_zone,
        "created_at": datetime.datetime.now().isoformat(),
        "deleted": False,
        "deleted_at": None,
        "hosts": hosts,
        "id": int(id),
        "metadata": {
            "availability_zone": availability_zone,
        },
        "name": name,
        "updated_at": None,
    }))
