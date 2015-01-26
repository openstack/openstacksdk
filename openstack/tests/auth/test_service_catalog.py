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

import testtools

from openstack.auth import service_catalog as catalog
from openstack.auth import service_filter
from openstack.compute import compute_service
from openstack import exceptions as exc
from openstack.identity import identity_service
from openstack.image import image_service
from openstack.network import network_service
from openstack.object_store import object_store_service
from openstack.tests.auth import common


class TestServiceCatalog(testtools.TestCase):
    def get_urls(self, sot):
        sf = service_filter.ServiceFilter(service_type='compute')
        exp = ["http://compute.region0.public/v1.1",
               "http://compute.region2.public/v1",
               "http://compute.region1.public/v2.0"]
        self.assertEqual(exp, sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='image')
        self.assertEqual(["http://image.region1.public/v2"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='identity')
        self.assertEqual(["http://identity.region1.public/v1.1/123123"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='object-store')
        self.assertEqual(["http://object-store.region1.public/"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='object-store',
                                          version='v9')
        self.assertEqual(["http://object-store.region1.public/v9"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='object-store')
        osf = object_store_service.ObjectStoreService()
        sf = sf.join(osf)
        self.assertEqual(["http://object-store.region1.public/v1"],
                         sot.get_urls(sf))

    def get_urls_name(self, sot):
        sf = service_filter.ServiceFilter(service_type='compute',
                                          service_name='nova')
        self.assertEqual(["http://compute.region1.public/v2.0"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='compute',
                                          service_name='nova2')
        self.assertEqual(["http://compute.region2.public/v1"],
                         sot.get_urls(sf))

    def get_urls_region(self, sot):
        sf = service_filter.ServiceFilter(service_type='compute',
                                          region='RegionTwo')
        self.assertEqual(["http://compute.region2.public/v1"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='compute',
                                          region='RegionOne')
        self.assertEqual(["http://compute.region1.public/v2.0"],
                         sot.get_urls(sf))

    def get_urls_visibility(self, sot):
        sf = service_filter.ServiceFilter(service_type='identity',
                                          visibility='admin')
        self.assertEqual(["http://identity.region1.admin/v1.1/123123"],
                         sot.get_urls(sf))
        sf = service_filter.ServiceFilter(service_type='identity',
                                          visibility='internal')
        self.assertEqual(
            ["http://identity.region1.internal/v1.1/123123"],
            sot.get_urls(sf)
        )
        sf = service_filter.ServiceFilter(service_type='identity',
                                          visibility='public')
        self.assertEqual(["http://identity.region1.public/v1.1/123123"],
                         sot.get_urls(sf))


class TestServiceCatalogV2(TestServiceCatalog):
    def test_catalog(self):
        sot = catalog.ServiceCatalogV2(common.TEST_SERVICE_CATALOG_V2)
        self.assertEqual(common.TEST_SERVICE_CATALOG_NORMALIZED,
                         sot.catalog)

    def test_catalog_empty(self):
        self.assertRaises(exc.EmptyCatalog, catalog.ServiceCatalogV2, None)

    def test_get_urls(self):
        sot = catalog.ServiceCatalogV2(common.TEST_SERVICE_CATALOG_V2)
        self.get_urls(sot)

    def test_get_urls_name(self):
        sot = catalog.ServiceCatalogV2(common.TEST_SERVICE_CATALOG_V2)
        self.get_urls_name(sot)

    def test_get_urls_region(self):
        sot = catalog.ServiceCatalogV2(common.TEST_SERVICE_CATALOG_V2)
        self.get_urls_region(sot)

    def test_get_urls_visibility(self):
        sot = catalog.ServiceCatalogV2(common.TEST_SERVICE_CATALOG_V2)
        self.get_urls_visibility(sot)


class TestServiceCatalogV3(TestServiceCatalog):
    def test_catalog(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        self.assertEqual(common.TEST_SERVICE_CATALOG_NORMALIZED,
                         sot.catalog)

    def test_catalog_empty(self):
        self.assertRaises(exc.EmptyCatalog, catalog.ServiceCatalog, None)

    def test_get_urls(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        self.get_urls(sot)

    def test_get_urls_name(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        self.get_urls_name(sot)

    def test_get_urls_region(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        self.get_urls_region(sot)

    def test_get_urls_visibility(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        self.get_urls_visibility(sot)

    def test_get_versions(self):
        sot = catalog.ServiceCatalog(common.TEST_SERVICE_CATALOG_V3)
        service = compute_service.ComputeService()
        self.assertEqual(['v1.1', 'v1', 'v2.0'], sot.get_versions(service))
        service = identity_service.IdentityService()
        self.assertEqual(['v1.1'], sot.get_versions(service))
        service = image_service.ImageService()
        self.assertEqual(['v2'], sot.get_versions(service))
        service = network_service.NetworkService()
        self.assertEqual(None, sot.get_versions(service))
        service = object_store_service.ObjectStoreService()
        self.assertEqual([], sot.get_versions(service))
