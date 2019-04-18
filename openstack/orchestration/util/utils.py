# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
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

import base64
import os

from six.moves.urllib import error
from six.moves.urllib import parse
from six.moves.urllib import request

from openstack import exceptions


def base_url_for_url(url):
    parsed = parse.urlparse(url)
    parsed_dir = os.path.dirname(parsed.path)
    return parse.urljoin(url, parsed_dir)


def normalise_file_path_to_url(path):
    if parse.urlparse(path).scheme:
        return path
    path = os.path.abspath(path)
    return parse.urljoin('file:', request.pathname2url(path))


def read_url_content(url):
    try:
        # TODO(mordred) Use requests
        content = request.urlopen(url).read()
    except error.URLError:
        raise exceptions.SDKException(
            'Could not fetch contents for %s' % url)

    if content:
        try:
            content = content.decode('utf-8')
        except ValueError:
            content = base64.encodestring(content)
    return content


def resource_nested_identifier(rsrc):
    nested_link = [l for l in rsrc.links or []
                   if l.get('rel') == 'nested']
    if nested_link:
        nested_href = nested_link[0].get('href')
        nested_identifier = nested_href.split("/")[-2:]
        return "/".join(nested_identifier)
