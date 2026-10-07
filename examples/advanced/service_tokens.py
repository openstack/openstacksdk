#!/usr/bin/env python3
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

"""Connect to an OpenStack cloud using service tokens.

Reads an oslo.config configuration file (defaulting to /tmp/service.conf, or
specified via --config-file) containing [cinder] and [service_user] sections.

Demonstrates sending a service token alongside the user token:
  X-Auth-Token: <cinder auth token>
  X-Service-Token: <nova service token>

Run with mitmweb/mitmproxy to inspect the outgoing headers::

    export HTTP_PROXY=http://127.0.0.1:8080
    python examples/advanced/service_tokens.py
"""

import sys

from keystoneauth1 import loading as ks_loading
from keystoneauth1 import service_token
from keystoneauth1 import session as ks_session
from oslo_config import cfg

import openstack.connection

CONF = cfg.ConfigOpts()


def _register_opts() -> None:
    # Register options for the target service client group ([cinder])
    cinder_group = cfg.OptGroup('cinder', title='Cinder Options')
    CONF.register_group(cinder_group)
    CONF.register_opts(
        [cfg.StrOpt('os_region_name', default='RegionOne')],
        group='cinder',
    )
    ks_loading.register_session_conf_options(CONF, 'cinder')
    ks_loading.register_auth_conf_options(CONF, 'cinder')

    # Register options for the service user token group ([service_user])
    service_user_group = cfg.OptGroup(
        'service_user', title='Service User Options'
    )
    CONF.register_group(service_user_group)
    CONF.register_opts(
        [cfg.BoolOpt('send_service_user_token', default=False)],
        group='service_user',
    )
    ks_loading.register_session_conf_options(CONF, 'service_user')
    ks_loading.register_auth_conf_options(CONF, 'service_user')


def main() -> None:
    _register_opts()
    CONF(sys.argv[1:], default_config_files=['/tmp/service.conf'])

    # Load auth plugins from configuration
    cinder_auth = ks_loading.load_auth_from_conf_options(CONF, 'cinder')
    service_auth = ks_loading.load_auth_from_conf_options(CONF, 'service_user')

    # Wrap auth plugins so both X-Auth-Token and X-Service-Token are sent
    auth = service_token.ServiceTokenAuthWrapper(
        user_auth=cinder_auth, service_auth=service_auth
    )
    sess = ks_session.Session(auth=auth)

    conn = openstack.connection.Connection(
        session=sess, region_name=CONF.cinder.os_region_name
    )

    print('Listing volume types...')
    try:
        vtypes = list(conn.block_storage.types())
        print(f'Found {len(vtypes)} volume type(s):')
        for vt in vtypes:
            print(f'  - {vt.name} ({vt.id})')
    except Exception as exc:
        print(f'ERROR: {exc}')


if __name__ == '__main__':
    main()
