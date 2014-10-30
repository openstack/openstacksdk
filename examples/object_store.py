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

from __future__ import print_function

import glob
import os
import sys

from examples import common
from openstack import connection

CONTAINER_HEADER = ("Name{0}| Bytes Used{1}| "
                    "Num Objects".format(13 * " ", 1 * " "))
CONTAINER_FORMAT = ("{0.name: <16} | {0.bytes: <10} | {0.count}")
OBJECT_HEADER = ("Name{0}| Bytes {1}| "
                 "Content-Type".format(27 * " ", 2 * " "))
OBJECT_FORMAT = ("{0.name: <30} | {0.bytes: <7} | {0.content_type}")


def list_containers(conn):
    print(CONTAINER_HEADER)
    print("=" * len(CONTAINER_HEADER))
    for container in conn.object_store.containers():
        print(CONTAINER_FORMAT.format(container))


def list_objects(conn, container):
    print(OBJECT_HEADER)
    print("=" * len(OBJECT_HEADER))
    for obj in conn.object_store.objects(container.decode("utf8")):
        print(OBJECT_FORMAT.format(obj))


def upload_directory(conn, directory, pattern):
    """Upload a directory to object storage.

    Given an OpenStack connection, a directory, and a file glob pattern,
    upload all files matching the pattern from that directory into a
    container named after the directory containing the files.
    """
    container_name = os.path.basename(os.path.realpath(directory))

    container = conn.object_store.create_container(
        container_name.decode("utf8"))

    for root, dirs, files in os.walk(directory):
        for file in glob.iglob(os.path.join(root, pattern)):
            with open(file, "rb") as f:
                ob = conn.object_store.create_object(data=f.read(),
                                                     obj=file.decode("utf8"),
                                                     container=container)
                print("Uploaded {0.name}".format(ob))


def main():
    # Add on to the common parser with a few options of our own.
    parser = common.option_parser()

    parser.add_argument("--list-containers", dest="list_containers",
                        action="store_true")
    parser.add_argument("--list-objects", dest="container")
    parser.add_argument("--upload-directory", dest="directory")
    parser.add_argument("--pattern", dest="pattern")

    opts = parser.parse_args()

    args = {
        'auth_plugin': opts.auth_plugin,
        'auth_url': opts.auth_url,
        'project_name': opts.project_name,
        'domain_name': opts.domain_name,
        'project_domain_name': opts.project_domain_name,
        'user_domain_name': opts.user_domain_name,
        'user_name': opts.user_name,
        'password': opts.password,
        'verify': opts.verify,
        'token': opts.token,
    }
    conn = connection.Connection(**args)

    if opts.list_containers:
        return list_containers(conn)
    elif opts.container:
        return list_objects(conn, opts.container)
    elif opts.directory and opts.pattern:
        return upload_directory(conn, opts.directory.decode("utf8"),
                                opts.pattern)
    else:
        print(parser.print_help())

    return -1

if __name__ == "__main__":
    sys.exit(main())
