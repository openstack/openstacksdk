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
fixtures
--------

Fixtures used for testing
"""

import warnings

import fixtures

from openstack import warnings as os_warnings


# TODO(stephenfin): Replace this with WarningsFilter from fixtures when it's
# released https://github.com/testing-cabal/fixtures/pull/50
class WarningsFixture(fixtures.Fixture):
    """Filters out warnings during test runs."""

    def setUp(self):
        super().setUp()

        self._original_warning_filters = warnings.filters[:]

        # enable user warnings as many libraries use this (it's the default)
        warnings.simplefilter("error", UserWarning)

        # enable deprecation warnings in general...
        warnings.simplefilter("once", DeprecationWarning)

        # ...but ignore our own deprecation warnings
        warnings.filterwarnings(
            "ignore",
            category=os_warnings.OpenStackDeprecationWarning,
        )
        warnings.filterwarnings(
            "ignore",
            category=os_warnings._RemovedInSDKWarning,
        )

        # also ignore our own general warnings
        warnings.filterwarnings(
            "ignore",
            category=os_warnings.OpenStackWarning,
        )

        self.addCleanup(self._reset_warning_filters)

    def _reset_warning_filters(self):
        warnings.filters[:] = self._original_warning_filters  # type: ignore[index]
