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

import yaml

from openstack.orchestration.util import template_format


SECTIONS = (
    PARAMETER_DEFAULTS,
    PARAMETERS,
    RESOURCE_REGISTRY,
    ENCRYPTED_PARAM_NAMES,
    EVENT_SINKS,
    PARAMETER_MERGE_STRATEGIES,
) = (
    'parameter_defaults',
    'parameters',
    'resource_registry',
    'encrypted_param_names',
    'event_sinks',
    'parameter_merge_strategies',
)


def parse(env_str):
    """Takes a string and returns a dict containing the parsed structure.

    This includes determination of whether the string is using the
    YAML format.
    """
    try:
        env = yaml.load(env_str, Loader=template_format.yaml_loader)  # noqa: S506
    except yaml.YAMLError:
        # NOTE(prazumovsky): we need to return more informative error for
        # user, so use SafeLoader, which return error message with template
        # snippet where error has been occurred.
        try:
            env = yaml.load(env_str, Loader=yaml.SafeLoader)
        except yaml.YAMLError as yea:
            raise ValueError(yea)
    else:
        if env is None:
            env = {}
        elif not isinstance(env, dict):
            raise ValueError(
                'The environment is not a valid YAML mapping data type.'
            )

    for param in env:
        if param not in SECTIONS:
            raise ValueError(f'environment has wrong section "{param}"')

    return env
