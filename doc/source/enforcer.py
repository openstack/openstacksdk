#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import importlib
import os

from bs4 import BeautifulSoup
from sphinx import errors
from sphinx.util import logging

LOG = logging.getLogger(__name__)

# NOTE: We do this because I can't find any way to pass "-v"
# into sphinx-build through pbr...
DEBUG = True if os.getenv("ENFORCER_DEBUG") else False

WRITTEN_METHODS = set()


class EnforcementError(errors.SphinxError):
    """A mismatch between what exists and what's documented"""
    category = "Enforcer"


def get_proxy_methods():
    """Return a set of public names on all proxies"""
    names = ["openstack.baremetal.v1._proxy",
             "openstack.clustering.v1._proxy",
             "openstack.block_storage.v2._proxy",
             "openstack.compute.v2._proxy",
             "openstack.database.v1._proxy",
             "openstack.identity.v2._proxy",
             "openstack.identity.v3._proxy",
             "openstack.image.v1._proxy",
             "openstack.image.v2._proxy",
             "openstack.key_manager.v1._proxy",
             "openstack.load_balancer.v2._proxy",
             "openstack.message.v2._proxy",
             "openstack.network.v2._proxy",
             "openstack.object_store.v1._proxy",
             "openstack.orchestration.v1._proxy",
             "openstack.workflow.v2._proxy"]

    modules = (importlib.import_module(name) for name in names)

    methods = set()
    for module in modules:
        # We're not going to use the Proxy for anything other than a `dir`
        # so just pass a dummy value so we can create the instance.
        instance = module.Proxy("")
        # We only document public names
        names = [name for name in dir(instance) if not name.startswith("_")]

        good_names = [module.__name__ + ".Proxy." + name for name in names]
        methods.update(good_names)

    return methods


def page_context(app, pagename, templatename, context, doctree):
    """Handle html-page-context-event

    This event is emitted once the builder has the contents to create
    an HTML page, but before the template is rendered. This is the point
    where we'll know what documentation is going to be written, so
    gather all of the method names that are about to be included
    so we can check which ones were or were not processed earlier
    by autodoc.
    """
    if "users/proxies" in pagename:
        soup = BeautifulSoup(context["body"], "html.parser")
        dts = soup.find_all("dt")
        ids = [dt.get("id") for dt in dts]

        written = 0
        for id in ids:
            if id is not None and "_proxy.Proxy" in id:
                WRITTEN_METHODS.add(id)
                written += 1

        if DEBUG:
            LOG.info("ENFORCER: Wrote %d proxy methods for %s" % (
                     written, pagename))


def build_finished(app, exception):
    """Handle build-finished event

    This event is emitted once the builder has written all of the output.
    At this point we just compare what we know was written to what we know
    exists within the modules and share the results.

    When enforcer_warnings_as_errors=True in conf.py, this method
    will raise EnforcementError on any failures in order to signal failure.
    """
    all_methods = get_proxy_methods()

    LOG.info("ENFORCER: %d proxy methods exist" % len(all_methods))
    LOG.info("ENFORCER: %d proxy methods written" % len(WRITTEN_METHODS))
    missing = all_methods - WRITTEN_METHODS

    missing_count = len(missing)
    LOG.info("ENFORCER: Found %d missing proxy methods "
             "in the output" % missing_count)

    # TODO(shade) This is spewing a bunch of content for missing thing that
    # are not actually missing. Leave it as info rather than warn so that the
    # gate doesn't break ... but we should figure out why this is broken and
    # fix it.
    # We also need to deal with Proxy subclassing keystoneauth.adapter.Adapter
    # now - some of the warnings come from Adapter elements.
    for name in sorted(missing):
        LOG.info("ENFORCER: %s was not included in the output" % name)

    if app.config.enforcer_warnings_as_errors and missing_count > 0:
        raise EnforcementError(
            "There are %d undocumented proxy methods" % missing_count)


def setup(app):
    app.add_config_value("enforcer_warnings_as_errors", False, "env")

    app.connect("html-page-context", page_context)
    app.connect("build-finished", build_finished)
