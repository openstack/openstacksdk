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

TEST_ADMIN_URL = 'http://identity.region1.admin/v1.1/123123'
TEST_DOMAIN_ID = '1'
TEST_DOMAIN_NAME = 'aDomain'
TEST_EXPIRES = '2020-01-01 00:00:10.000123+00:00'
TEST_PASS = 'wasspord'
TEST_PROJECT_ID = 'pid'
TEST_PROJECT_NAME = 'pname'
TEST_SUBJECT = 'subjay'
TEST_TOKEN = 'atoken'
TEST_TENANT_ID = 'tid'
TEST_TENANT_NAME = 'tname'
TEST_TRUST_ID = 'trusty'
TEST_USER = 'youzer'
TEST_USER_ID = 'youid'

TEST_SERVICE_CATALOG_V2 = [
    {
        "endpoints": [{
            "adminURL": "http://compute.region0.admin/v1.1/",
            "internalURL": "http://compute.region0.internal/v1.1/",
            "publicURL": "http://compute.region0.public/v1.1/",
        }],
        "type": "compute",
        "name": "nova0"
    }, {
        "endpoints": [{
            "adminURL": "http://compute.region2.admin/v1/",
            "region": "RegionTwo",
            "internalURL": "http://compute.region2.internal/v1/",
            "publicURL": "http://compute.region2.public/v1/",
        }],
        "type": "compute",
        "name": "nova2"
    }, {
        "endpoints": [{
            "adminURL": "http://compute.region1.admin/v2.0/",
            "region": "RegionOne",
            "internalURL": "http://compute.region1.internal/v2.0/",
            "publicURL": "http://compute.region1.public/v2.0/",
        }],
        "type": "compute",
        "name": "nova"
    }, {
        "endpoints": [{
            "adminURL": "http://image.region1.admin/v2",
            "region": "RegionOne",
            "internalURL": "http://image.region1.internal/v2",
            "publicURL": "http://image.region1.public/v2",
        }],
        "type": "image",
        "name": "glance"
    }, {
        "endpoints": [{
            "adminURL": TEST_ADMIN_URL,
            "region": "RegionOne",
            "internalURL": "http://identity.region1.internal/v1.1/123123",
            "publicURL": "http://identity.region1.public/v1.1/123123",
        }],
        "type": "identity",
        "name": "keystone"
    }, {
        "endpoints": [{
            "adminURL": "http://object-store.region1.admin/",
            "region": "RegionOne",
            "internalURL": "http://object-store.region1.internal/",
            "publicURL": "http://object-store.region1.public/",
        }],
        "type": "object-store",
        "name": "swift"
    }]
TEST_SERVICE_CATALOG_NORMALIZED = [
    {
        "endpoints": [{
            "interface": "public",
            "url": "http://compute.region0.public/%(version)s",
            'version': 'v1.1',
        }, {
            "interface": "internal",
            "url": "http://compute.region0.internal/%(version)s",
            'version': 'v1.1',
        }, {
            "interface": "admin",
            "url": "http://compute.region0.admin/%(version)s",
            'version': 'v1.1',
        }],
        "type": "compute",
        "name": "nova0"
    }, {
        "endpoints": [{
            "interface": "public",
            "region": "RegionTwo",
            "url": "http://compute.region2.public/%(version)s",
            'version': 'v1',
        }, {
            "interface": "internal",
            "region": "RegionTwo",
            "url": "http://compute.region2.internal/%(version)s",
            'version': 'v1',
        }, {
            "interface": "admin",
            "region": "RegionTwo",
            "url": "http://compute.region2.admin/%(version)s",
            'version': 'v1',
        }],
        "type": "compute",
        "name": "nova2"
    }, {
        "endpoints": [{
            "interface": "public",
            "region": "RegionOne",
            "url": "http://compute.region1.public/%(version)s",
            'version': 'v2.0',
        }, {
            "interface": "internal",
            "region": "RegionOne",
            "url": "http://compute.region1.internal/%(version)s",
            'version': 'v2.0',
        }, {
            "interface": "admin",
            "region": "RegionOne",
            "url": "http://compute.region1.admin/%(version)s",
            'version': 'v2.0',
        }],
        "type": "compute",
        "name": "nova"
    }, {
        "endpoints": [{
            "interface": "public",
            "region": "RegionOne",
            "url": "http://image.region1.public/%(version)s",
            'version': 'v2',
        }, {
            "interface": "internal",
            "region": "RegionOne",
            "url": "http://image.region1.internal/%(version)s",
            'version': 'v2',
        }, {
            "interface": "admin",
            "region": "RegionOne",
            "url": "http://image.region1.admin/%(version)s",
            'version': 'v2',
        }],
        "type": "image",
        "name": "glance",
    }, {
        "endpoints": [{
            "interface": "public",
            "region": "RegionOne",
            "url": "http://identity.region1.public/%(version)s/123123",
            'version': 'v1.1',
        }, {
            "interface": "internal",
            "region": "RegionOne",
            "url": "http://identity.region1.internal/%(version)s/123123",
            'version': 'v1.1',
        }, {
            "interface": "admin",
            "region": "RegionOne",
            "url": "http://identity.region1.admin/%(version)s/123123",
            'version': 'v1.1',
        }],
        "type": "identity",
        "name": "keystone",
    }, {
        "endpoints": [{
            "interface": "public",
            "region": "RegionOne",
            "url": "http://object-store.region1.public/%(version)s",
        }, {
            "interface": "internal",
            "region": "RegionOne",
            "url": "http://object-store.region1.internal/%(version)s",
        }, {
            "interface": "admin",
            "region": "RegionOne",
            "url": "http://object-store.region1.admin/%(version)s",
        }],
        "type": "object-store",
        "name": "swift",
    }]
TEST_RESPONSE_DICT_V2 = {
    "access": {
        "token": {
            "expires": TEST_EXPIRES,
            "id": TEST_TOKEN,
            "tenant": {
                "id": TEST_TENANT_ID
            },
        },
        "user": {
            "id": TEST_USER_ID
        },
        "serviceCatalog": TEST_SERVICE_CATALOG_V2,
    },
}


TEST_SERVICE_CATALOG_V3 = [
    {
        "endpoints": [{
            "url": "http://compute.region0.public/v1.1/",
            "interface": "public"
        }, {
            "url": "http://compute.region0.internal/v1.1/",
            "interface": "internal"
        }, {
            "url": "http://compute.region0.admin/v1.1/",
            "interface": "admin"
        }],
        "type": "compute",
        "name": "nova0",
    }, {
        "endpoints": [{
            "url": "http://compute.region2.public/v1/",
            "region": "RegionTwo",
            "interface": "public"
        }, {
            "url": "http://compute.region2.internal/v1/",
            "region": "RegionTwo",
            "interface": "internal"
        }, {
            "url": "http://compute.region2.admin/v1/",
            "region": "RegionTwo",
            "interface": "admin"
        }],
        "type": "compute",
        "name": "nova2",
    }, {
        "endpoints": [{
            "url": "http://compute.region1.public/v2.0/",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://compute.region1.internal/v2.0/",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://compute.region1.admin/v2.0/",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "compute",
        "name": "nova",
    }, {
        "endpoints": [{
            "url": "http://image.region1.public/v2",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://image.region1.internal/v2",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://image.region1.admin/v2",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "image",
        "name": "glance",
    }, {
        "endpoints": [{
            "url": "http://identity.region1.public/v1.1/123123",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://identity.region1.internal/v1.1/123123",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://identity.region1.admin/v1.1/123123",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "identity",
        "name": "keystone",
    }, {
        "endpoints": [{
            "url": "http://object-store.region1.public/",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://object-store.region1.internal/",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://object-store.region1.admin/",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "object-store",
        "name": "swift",
    }]

TEST_RESPONSE_DICT_V3 = {
    "token": {
        "methods": [
            "token",
            "password"
        ],

        "expires_at": TEST_EXPIRES,
        "project": {
            "domain": {
                "id": TEST_DOMAIN_ID,
                "name": TEST_DOMAIN_NAME
            },
            "id": TEST_PROJECT_ID,
            "name": TEST_PROJECT_NAME
        },
        "user": {
            "domain": {
                "id": TEST_DOMAIN_ID,
                "name": TEST_DOMAIN_NAME
            },
            "id": TEST_USER_ID,
            "name": TEST_USER
        },
        "issued_at": "2013-05-29T16:55:21.468960Z",
        "catalog": TEST_SERVICE_CATALOG_V3
    },
}
