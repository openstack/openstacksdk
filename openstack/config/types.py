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

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    import prometheus_client


class ClientConfig(TypedDict):
    force_ipv4: bool
    ...


class StatsdConfig(TypedDict, total=False):
    host: str | None
    # port may be a string when sourced from the configuration file
    port: int | str | None
    prefix: str | None


class InfluxDBConfig(TypedDict, total=False):
    host: str | None
    # port may be a string when sourced from the configuration file
    port: int | str | None
    username: str | None
    password: str | None
    database: str | None
    measurement: str | None
    timeout: int | float | None
    use_udp: str | bool | None
    additional_metric_tags: dict[str, str]


class PrometheusConfig(TypedDict, total=False):
    collector_registry: 'prometheus_client.CollectorRegistry | None'
