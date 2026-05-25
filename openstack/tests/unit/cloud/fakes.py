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
fakes
-----

Fakes used for testing
"""

import hashlib
import json

PROJECT_ID = '1c36b64c840a42cd9e9b931a369337f0'
COMPUTE_ENDPOINT = 'https://compute.example.com/v2.1'
NO_MD5 = '93b885adfe0da089cdf634904fd59f71'
NO_SHA256 = '6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d'


def make_fake_flavor(flavor_id, name, ram=100, disk=1600, vcpus=24):
    return {
        'OS-FLV-DISABLED:disabled': False,
        'OS-FLV-EXT-DATA:ephemeral': 0,
        'disk': disk,
        'id': flavor_id,
        'links': [
            {
                'href': f'{COMPUTE_ENDPOINT}/flavors/{flavor_id}',
                'rel': 'self',
            },
            {
                'href': f'{COMPUTE_ENDPOINT}/flavors/{flavor_id}',
                'rel': 'bookmark',
            },
        ],
        'name': name,
        'os-flavor-access:is_public': True,
        'ram': ram,
        'rxtx_factor': 1.0,
        'swap': 0,
        'vcpus': vcpus,
    }


FLAVOR_ID = '0c1d9008-f546-4608-9e8f-f8bdaec8dddd'
FAKE_FLAVOR = make_fake_flavor(FLAVOR_ID, 'vanilla')
CHOCOLATE_FLAVOR_ID = '0c1d9008-f546-4608-9e8f-f8bdaec8ddde'
FAKE_CHOCOLATE_FLAVOR = make_fake_flavor(
    CHOCOLATE_FLAVOR_ID, 'chocolate', ram=200
)
STRAWBERRY_FLAVOR_ID = '0c1d9008-f546-4608-9e8f-f8bdaec8dddf'
FAKE_STRAWBERRY_FLAVOR = make_fake_flavor(
    STRAWBERRY_FLAVOR_ID, 'strawberry', ram=300
)
FAKE_FLAVOR_LIST = [FAKE_FLAVOR, FAKE_CHOCOLATE_FLAVOR, FAKE_STRAWBERRY_FLAVOR]


def make_fake_server(
    server_id,
    name,
    status='ACTIVE',
    admin_pass=None,
    addresses=None,
    image=None,
    flavor=None,
):
    if addresses is None:
        if status == 'ACTIVE':
            addresses = {
                "private": [
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 6,
                        "addr": "fddb:b018:307:0:f816:3eff:fedf:b08d",
                        "OS-EXT-IPS:type": "fixed",
                    },
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 4,
                        "addr": "10.1.0.9",
                        "OS-EXT-IPS:type": "fixed",
                    },
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:df:b0:8d",
                        "version": 4,
                        "addr": "172.24.5.5",
                        "OS-EXT-IPS:type": "floating",
                    },
                ]
            }
        else:
            addresses = {}
    if image is None:
        image = {"id": "217f3ab1-03e0-4450-bf27-63d52b421e9e", "links": []}
    if flavor is None:
        flavor = {"id": "64", "links": []}

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
        "config_drive": "True",
    }
    if admin_pass:
        server['adminPass'] = admin_pass
    return json.loads(json.dumps(server))


def make_fake_image(
    image_id=None,
    md5=NO_MD5,
    sha256=NO_SHA256,
    status='active',
    image_name='fake_image',
    data=None,
    checksum='ee36e35a297980dee1b514de9803ec6d',
):
    if data:
        md5_hash = hashlib.md5(usedforsecurity=False)
        sha256_hash = hashlib.sha256()
        sha512_hash = hashlib.sha512()
        with open(data, 'rb') as file_obj:
            for chunk in iter(lambda: file_obj.read(8192), b''):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                sha512_hash.update(chunk)
        md5 = md5_hash.hexdigest()
        sha256 = sha256_hash.hexdigest()
        sha512 = sha512_hash.hexdigest()
    else:
        sha512 = None
    return {
        'image_state': 'available',
        'container_format': 'bare',
        'min_ram': 0,
        'ramdisk_id': 'fake_ramdisk_id',
        'updated_at': '2016-02-10T05:05:02Z',
        'file': '/v2/images/' + image_id + '/file',
        'size': 3402170368,
        'image_type': 'snapshot',
        'disk_format': 'qcow2',
        'id': image_id,
        'schema': '/v2/schemas/image',
        'status': status,
        'tags': [],
        'visibility': 'private',
        'locations': [
            {'url': 'http://127.0.0.1/images/' + image_id, 'metadata': {}}
        ],
        'min_disk': 40,
        'virtual_size': None,
        'name': image_name,
        'checksum': md5 or checksum,
        'created_at': '2016-02-10T05:03:11Z',
        'owner_specified.openstack.md5': md5 or NO_MD5,
        'owner_specified.openstack.sha256': sha256 or NO_SHA256,
        'owner_specified.openstack.object': f'images/{image_name}',
        'protected': False,
        # Add secure hash fields (os_hash_algo and os_hash_value)
        # Default to sha512 if data was provided, otherwise None
        'os_hash_algo': 'sha512' if sha512 else None,
        'os_hash_value': sha512 if sha512 else None,
    }


def make_fake_server_group(id, name, policies):
    return json.loads(
        json.dumps(
            {
                'id': id,
                'name': name,
                'policies': policies,
                'members': [],
                'metadata': {},
            }
        )
    )


def make_fake_hypervisor(id, name):
    return json.loads(
        json.dumps(
            {
                'id': id,
                'hypervisor_hostname': name,
                'state': 'up',
                'status': 'enabled',
                "cpu_info": {
                    "arch": "x86_64",
                    "model": "Nehalem",
                    "vendor": "Intel",
                    "features": ["pge", "clflush"],
                    "topology": {"cores": 1, "threads": 1, "sockets": 4},
                },
                "current_workload": 0,
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
                "service": {"host": "host1", "id": 7, "disabled_reason": None},
                "vcpus": 1,
                "vcpus_used": 0,
            }
        )
    )


class FakeVolume:
    def __init__(self, id, status, name, attachments=[], size=75):
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
        self.updated_at = None
        self.source_volid = '12345'
        self.metadata = {}


class FakeVolumeSnapshot:
    def __init__(self, id, status, name, description, size=75):
        self.id = id
        self.status = status
        self.name = name
        self.description = description
        self.size = size
        self.created_at = '1900-01-01 12:34:56'
        self.updated_at = None
        self.volume_id = '12345'
        self.metadata = {}
        self.is_forced = False
