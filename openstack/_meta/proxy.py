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

# Inspired by code from
# https://github.com/micheles/decorator/blob/master/src/decorator.py
# which is MIT licensed.

from openstack._meta import _proxy_templates
from openstack import resource


def compile_function(evaldict, action, module, **kwargs):
    "Make a new functions"

    src = _proxy_templates.get_source_template(action, **kwargs)

    # Ensure each generated block of code has a unique filename for profilers
    # (such as cProfile) that depend on the tuple of (<filename>,
    # <definition line>, <function name>) being unique.
    filename = '<generated-{module}>'.format(module=module)
    code = compile(src, filename, 'exec')
    exec(code, evaldict)
    func = evaldict[action]
    func.__source__ = src
    return func


def add_function(dct, func, action, args, name_template='{action}_{name}'):
    func_name = name_template.format(action=action, **args)
    # If the class has the function already, don't override it
    if func_name in dct:
        func_name = '_generated_' + func_name
    func.__name__ = func_name
    func.__qualname__ = func_name
    func.__doc__ = _proxy_templates.get_doc_template(action, **args)
    func.__module__ = args['module']
    dct[func_name] = func


def expand_classname(res):
    return '{module}.{name}'.format(module=res.__module__, name=res.__name__)


class ProxyMeta(type):
    """Metaclass that generates standard methods based on Resources.

    Each service has a set of Resources which define the fundamental
    qualities of the remote resources. A large portion of the methods
    on Proxy classes are boilerplate.

    This metaclass reads the definition of the Proxy class and looks for
    Resource classes attached to it. It then checks them to see which
    operations are allowed by looking at the ``allow_`` flags. Based on that,
    it generates the standard methods and adds them to the class.

    If a method exists on the class when it is read, the generated method
    does not overwrite the existing method. Instead, it is attached as
    ``_generated_{method_name}``. This allows people to either write
    specific proxy methods and completely ignore the generated method,
    or to write specialized methods that then delegate action to the generated
    method.

    Since this is done as a metaclass at class object creation time,
    things like sphinx continue to work.
    """
    def __new__(meta, name, bases, dct):
        # Build up a list of resource classes attached to the Proxy
        resources = {}
        details = {}
        for k, v in dct.items():
            if isinstance(v, type) and issubclass(v, resource.Resource):
                if v.detail_for:
                    details[v.detail_for.__name__] = v
                else:
                    resources[v.__name__] = v

        for resource_name, res in resources.items():
            resource_class = expand_classname(res)
            detail = details.get(resource_name, res)
            detail_name = detail.__name__
            detail_class = expand_classname(detail)

            lower_name = resource_name.lower()
            plural_name = getattr(res, 'plural_name', lower_name + 's')
            args = dict(
                resource_name=resource_name,
                resource_class=resource_class,
                name=lower_name,
                module=res.__module__,
                detail_name=detail_name,
                detail_class=detail_class,
                plural_name=plural_name,
            )
            # Generate unbound methods from the template strings.
            # We have to do a compile step rather than using somthing
            # like existing function objects wrapped with closures
            # because of the argument naming pattern for delete and update.
            # You can't really change an argument name programmatically,
            # at least not that I've been able to find.
            # We pass in a copy of the dct dict so that the exec step can
            # be done in the context of the class the methods will be attached
            # to. This allows name resolution to work properly.
            for action in ('create', 'get', 'update', 'delete'):
                if getattr(res, 'allow_{action}'.format(action=action)):
                    func = compile_function(dct.copy(), action, **args)
                    add_function(dct, func, action, args)
            if res.allow_list:
                func = compile_function(dct.copy(), 'find', **args)
                add_function(dct, func, 'find', args)
                func = compile_function(dct.copy(), 'list', **args)
                add_function(dct, func, 'list', args, plural_name)

        return super(ProxyMeta, meta).__new__(meta, name, bases, dct)
