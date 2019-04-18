# Copyright 2012 OpenStack Foundation
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

import collections
import json
import six
from six.moves.urllib import parse
from six.moves.urllib import request

from openstack.orchestration.util import environment_format
from openstack.orchestration.util import template_format
from openstack.orchestration.util import utils
from openstack import exceptions


def get_template_contents(template_file=None, template_url=None,
                          template_object=None, object_request=None,
                          files=None, existing=False):

    is_object = False
    tpl = None

    # Transform a bare file path to a file:// URL.
    if template_file:
        template_url = utils.normalise_file_path_to_url(template_file)

    if template_url:
        tpl = request.urlopen(template_url).read()

    elif template_object:
        is_object = True
        template_url = template_object
        tpl = object_request and object_request('GET',
                                                template_object)
    elif existing:
        return {}, None
    else:
        raise exceptions.SDKException(
            'Must provide one of template_file,'
            ' template_url or template_object')

    if not tpl:
        raise exceptions.SDKException(
            'Could not fetch template from %s' % template_url)

    try:
        if isinstance(tpl, six.binary_type):
            tpl = tpl.decode('utf-8')
        template = template_format.parse(tpl)
    except ValueError as e:
        raise exceptions.SDKException(
            'Error parsing template %(url)s %(error)s' %
            {'url': template_url, 'error': e})

    tmpl_base_url = utils.base_url_for_url(template_url)
    if files is None:
        files = {}
    resolve_template_get_files(template, files, tmpl_base_url, is_object,
                               object_request)
    return files, template


def resolve_template_get_files(template, files, template_base_url,
                               is_object=False, object_request=None):

    def ignore_if(key, value):
        if key != 'get_file' and key != 'type':
            return True
        if not isinstance(value, six.string_types):
            return True
        if (key == 'type'
                and not value.endswith(('.yaml', '.template'))):
            return True
        return False

    def recurse_if(value):
        return isinstance(value, (dict, list))

    get_file_contents(template, files, template_base_url,
                      ignore_if, recurse_if, is_object, object_request)


def is_template(file_content):
    try:
        if isinstance(file_content, six.binary_type):
            file_content = file_content.decode('utf-8')
        template_format.parse(file_content)
    except (ValueError, TypeError):
        return False
    return True


def get_file_contents(from_data, files, base_url=None,
                      ignore_if=None, recurse_if=None,
                      is_object=False, object_request=None):

    if recurse_if and recurse_if(from_data):
        if isinstance(from_data, dict):
            recurse_data = from_data.values()
        else:
            recurse_data = from_data
        for value in recurse_data:
            get_file_contents(value, files, base_url, ignore_if, recurse_if,
                              is_object, object_request)

    if isinstance(from_data, dict):
        for key, value in from_data.items():
            if ignore_if and ignore_if(key, value):
                continue

            if base_url and not base_url.endswith('/'):
                base_url = base_url + '/'

            str_url = parse.urljoin(base_url, value)
            if str_url not in files:
                if is_object and object_request:
                    file_content = object_request('GET', str_url)
                else:
                    file_content = utils.read_url_content(str_url)
                if is_template(file_content):
                    if is_object:
                        template = get_template_contents(
                            template_object=str_url, files=files,
                            object_request=object_request)[1]
                    else:
                        template = get_template_contents(
                            template_url=str_url, files=files)[1]
                    file_content = json.dumps(template)
                files[str_url] = file_content
            # replace the data value with the normalised absolute URL
            from_data[key] = str_url


def deep_update(old, new):
    '''Merge nested dictionaries.'''

    # Prevents an error if in a previous iteration
    # old[k] = None but v[k] = {...},
    if old is None:
        old = {}

    for k, v in new.items():
        if isinstance(v, collections.Mapping):
            r = deep_update(old.get(k, {}), v)
            old[k] = r
        else:
            old[k] = new[k]
    return old


def process_multiple_environments_and_files(env_paths=None, template=None,
                                            template_url=None,
                                            env_path_is_object=None,
                                            object_request=None,
                                            env_list_tracker=None):
    """Reads one or more environment files.

    Reads in each specified environment file and returns a dictionary
    of the filenames->contents (suitable for the files dict)
    and the consolidated environment (after having applied the correct
    overrides based on order).

    If a list is provided in the env_list_tracker parameter, the behavior
    is altered to take advantage of server-side environment resolution.
    Specifically, this means:

    * Populating env_list_tracker with an ordered list of environment file
      URLs to be passed to the server
    * Including the contents of each environment file in the returned
      files dict, keyed by one of the URLs in env_list_tracker

    :param env_paths: list of paths to the environment files to load; if
           None, empty results will be returned
    :type  env_paths: list or None
    :param template: unused; only included for API compatibility
    :param template_url: unused; only included for API compatibility
    :param env_list_tracker: if specified, environment filenames will be
           stored within
    :type  env_list_tracker: list or None
    :return: tuple of files dict and a dict of the consolidated environment
    :rtype:  tuple
    """
    merged_files = {}
    merged_env = {}

    # If we're keeping a list of environment files separately, include the
    # contents of the files in the files dict
    include_env_in_files = env_list_tracker is not None

    if env_paths:
        for env_path in env_paths:
            files, env = process_environment_and_files(
                env_path=env_path,
                template=template,
                template_url=template_url,
                env_path_is_object=env_path_is_object,
                object_request=object_request,
                include_env_in_files=include_env_in_files)

            # 'files' looks like {"filename1": contents, "filename2": contents}
            # so a simple update is enough for merging
            merged_files.update(files)

            # 'env' can be a deeply nested dictionary, so a simple update is
            # not enough
            merged_env = deep_update(merged_env, env)

            if env_list_tracker is not None:
                env_url = utils.normalise_file_path_to_url(env_path)
                env_list_tracker.append(env_url)

    return merged_files, merged_env


def process_environment_and_files(env_path=None,
                                  template=None,
                                  template_url=None,
                                  env_path_is_object=None,
                                  object_request=None,
                                  include_env_in_files=False):
    """Loads a single environment file.

    Returns an entry suitable for the files dict which maps the environment
    filename to its contents.

    :param env_path: full path to the file to load
    :type  env_path: str or None
    :param include_env_in_files: if specified, the raw environment file itself
           will be included in the returned files dict
    :type  include_env_in_files: bool
    :return: tuple of files dict and the loaded environment as a dict
    :rtype:  (dict, dict)
    """
    files = {}
    env = {}

    is_object = env_path_is_object and env_path_is_object(env_path)

    if is_object:
        raw_env = object_request and object_request('GET', env_path)
        env = environment_format.parse(raw_env)
        env_base_url = utils.base_url_for_url(env_path)

        resolve_environment_urls(
            env.get('resource_registry'),
            files,
            env_base_url, is_object=True, object_request=object_request)

    elif env_path:
        env_url = utils.normalise_file_path_to_url(env_path)
        env_base_url = utils.base_url_for_url(env_url)
        raw_env = request.urlopen(env_url).read()

        env = environment_format.parse(raw_env)

        resolve_environment_urls(
            env.get('resource_registry'),
            files,
            env_base_url)

        if include_env_in_files:
            files[env_url] = json.dumps(env)

    return files, env


def resolve_environment_urls(resource_registry, files, env_base_url,
                             is_object=False, object_request=None):
    """Handles any resource URLs specified in an environment.

    :param resource_registry: mapping of type name to template filename
    :type  resource_registry: dict
    :param files: dict to store loaded file contents into
    :type  files: dict
    :param env_base_url: base URL to look in when loading files
    :type  env_base_url: str or None
    """
    if resource_registry is None:
        return

    rr = resource_registry
    base_url = rr.get('base_url', env_base_url)

    def ignore_if(key, value):
        if key == 'base_url':
            return True
        if isinstance(value, dict):
            return True
        if '::' in value:
            # Built in providers like: "X::Compute::Server"
            # don't need downloading.
            return True
        if key in ['hooks', 'restricted_actions']:
            return True

    get_file_contents(rr, files, base_url, ignore_if,
                      is_object=is_object, object_request=object_request)

    for res_name, res_dict in rr.get('resources', {}).items():
        res_base_url = res_dict.get('base_url', base_url)
        get_file_contents(
            res_dict, files, res_base_url, ignore_if,
            is_object=is_object, object_request=object_request)
