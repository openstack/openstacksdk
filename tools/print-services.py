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
from openstack import service_description

_logger = _log.setup_logging('openstack')
_service_type_manager = os_service_types.ServiceTypes()


def make_names():
    imports = ['from openstack import service_description']
    services = []

    for service in _service_type_manager.services:
        service_type = service['service_type']
        if service_type == 'ec2-api':
            # NOTE(mordred) It doesn't make any sense to use ec2-api
            # from openstacksdk. The credentials API calls are all calls
            # on identity endpoints.
            continue
        desc_class = _find_service_description_class(service_type)

        st = service_type.replace('-', '_')

        if desc_class.__module__ != 'openstack.service_description':
            base_mod, dm = desc_class.__module__.rsplit('.', 1)
            imports.append(
                'from {base_mod} import {dm}'.format(
                    base_mod=base_mod,
                    dm=dm))
        else:
            dm = 'service_description'

        dc = desc_class.__name__
        services.append(
            "{st} = {dm}.{dc}(service_type='{service_type}')".format(
                st=st, dm=dm, dc=dc, service_type=service_type),
        )

        # Register the descriptor class with every known alias. Don't
        # add doc strings though - although they are supported, we don't
        # want to give anybody any bad ideas. Making a second descriptor
        # does not introduce runtime cost as the descriptors all use
        # the same _proxies dict on the instance.
        for alias_name in _get_aliases(st):
            if alias_name[-1].isdigit():
                continue
            services.append(
                '{alias_name} = {st}'.format(
                    alias_name=alias_name,
                    st=st))
        services.append('')
    print("# Generated file, to change, run tools/print-services.py")
    for imp in sorted(imports):
        print(imp)
    print('\n')
    print("class ServicesMixin:\n")
    for service in services:
        if service:
            print("    {service}".format(service=service))
        else:
            print()


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
    all_aliases = set()
    for alias in all_types:
        all_aliases.add(alias.replace('-', '_'))
    return all_aliases


def _find_service_description_class(service_type):
    package_name = 'openstack.{service_type}'.format(
        service_type=service_type).replace('-', '_')
    module_name = service_type.replace('-', '_') + '_service'
    class_name = ''.join(
        [part.capitalize() for part in module_name.split('_')])
    try:
        import_name = '.'.join([package_name, module_name])
        service_description_module = importlib.import_module(import_name)
    except ImportError as e:
        # ImportWarning is ignored by default. This warning is here
        # as an opt-in for people trying to figure out why something
        # didn't work.
        warnings.warn(
            "Could not import {service_type} service description: {e}".format(
                service_type=service_type, e=str(e)),
            ImportWarning)
        return service_description.ServiceDescription
    # There are no cases in which we should have a module but not the class
    # inside it.
    service_description_class = getattr(service_description_module, class_name)
    return service_description_class


make_names()
