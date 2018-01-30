# Copyright 2018 Red Hat, Inc.
#
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

import importlib
import warnings

import os_service_types

from openstack import _log
from openstack import proxy
from openstack import service_description

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()
_DOC_TEMPLATE = (
    ":class:`{class_name}` for {service_type} aka {project}")
_PROXY_TEMPLATE = """Proxy for {service_type} aka {project}

This proxy object could be an instance of
{class_doc_strings}
depending on client configuration and which version of the service is
found on remotely on the cloud.
"""


class ConnectionMeta(type):
    def __new__(meta, name, bases, dct):
        for service in _service_type_manager.services:
            service_type = service['service_type']
            if service_type == 'ec2-api':
                # NOTE(mordred) It doesn't make any sense to use ec2-api
                # from openstacksdk. The credentials API calls are all calls
                # on identity endpoints.
                continue
            desc_class = service_description.ServiceDescription
            service_filter_class = _find_service_filter_class(service_type)
            descriptor_args = {'service_type': service_type}
            if service_filter_class:
                desc_class = service_description.OpenStackServiceDescription
                descriptor_args['service_filter_class'] = service_filter_class
                class_names = service_filter_class._get_proxy_class_names()
                if len(class_names) == 1:
                    doc = _DOC_TEMPLATE.format(
                        class_name="{service_type} Proxy <{name}>".format(
                            service_type=service_type, name=class_names[0]),
                        **service)
                else:
                    class_doc_strings = "\n".join([
                        ":class:`{class_name}`".format(class_name=class_name)
                        for class_name in class_names])
                    doc = _PROXY_TEMPLATE.format(
                        class_doc_strings=class_doc_strings, **service)
            else:
                descriptor_args['proxy_class'] = proxy.Proxy
                doc = _DOC_TEMPLATE.format(
                    class_name='~openstack.proxy.Proxy', **service)
            descriptor = desc_class(**descriptor_args)
            descriptor.__doc__ = doc
            dct[service_type.replace('-', '_')] = descriptor

            # Register the descriptor class with every known alias. Don't
            # add doc strings though - although they are supported, we don't
            # want to give anybody any bad ideas. Making a second descriptor
            # does not introduce runtime cost as the descriptors all use
            # the same _proxies dict on the instance.
            for alias_name in _get_aliases(service_type):
                if alias_name[-1].isdigit():
                    continue
                alias_descriptor = desc_class(**descriptor_args)
                dct[alias_name.replace('-', '_')] = alias_descriptor
        return super(ConnectionMeta, meta).__new__(meta, name, bases, dct)


def _get_aliases(service_type, aliases=None):
    # We make connection attributes for all official real type names
    # and aliases. Three services have names they were called by in
    # openstacksdk that are not covered by Service Types Authority aliases.
    # Include them here - but take heed, no additional values should ever
    # be added to this list.
    # that were only used in openstacksdk resource naming.
    LOCAL_ALIASES = {
        'baremetal': 'bare_metal',
        'block_storage': 'block_store',
        'clustering': 'cluster',
    }
    all_types = set(_service_type_manager.get_aliases(service_type))
    if aliases:
        all_types.update(aliases)
    if service_type in LOCAL_ALIASES:
        all_types.add(LOCAL_ALIASES[service_type])
    return all_types


def _find_service_filter_class(service_type):
    package_name = 'openstack.{service_type}'.format(
        service_type=service_type).replace('-', '_')
    module_name = service_type.replace('-', '_') + '_service'
    class_name = ''.join(
        [part.capitalize() for part in module_name.split('_')])
    try:
        import_name = '.'.join([package_name, module_name])
        service_filter_module = importlib.import_module(import_name)
    except ImportError as e:
        # ImportWarning is ignored by default. This warning is here
        # as an opt-in for people trying to figure out why something
        # didn't work.
        warnings.warn(
            "Could not import {service_type} service filter: {e}".format(
                service_type=service_type, e=str(e)),
            ImportWarning)
        return None
    # There are no cases in which we should have a module but not the class
    # inside it.
    service_filter_class = getattr(service_filter_module, class_name)
    return service_filter_class
