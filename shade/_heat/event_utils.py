# Copyright 2015 Red Hat Inc.
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

import time

from shade._heat import utils
import heatclient.exc as exc


def get_events(hc, stack_id, event_args, nested_depth=0,
               marker=None, limit=None):
    event_args = dict(event_args)
    if marker:
        event_args['marker'] = marker
    if limit:
        event_args['limit'] = limit
    if not nested_depth:
        # simple call with no nested_depth
        return _get_stack_events(hc, stack_id, event_args)

    # assume an API which supports nested_depth
    event_args['nested_depth'] = nested_depth
    events = _get_stack_events(hc, stack_id, event_args)

    if not events:
        return events

    first_links = getattr(events[0], 'links', [])
    root_stack_link = [l for l in first_links
                       if l.get('rel') == 'root_stack']
    if root_stack_link:
        # response has a root_stack link, indicating this is an API which
        # supports nested_depth
        return events

    # API doesn't support nested_depth, do client-side paging and recursive
    # event fetch
    marker = event_args.pop('marker', None)
    limit = event_args.pop('limit', None)
    event_args.pop('nested_depth', None)
    events = _get_stack_events(hc, stack_id, event_args)
    events.extend(_get_nested_events(hc, nested_depth,
                                     stack_id, event_args))
    # Because there have been multiple stacks events mangled into
    # one list, we need to sort before passing to print_list
    # Note we can't use the prettytable sortby_index here, because
    # the "start" option doesn't allow post-sort slicing, which
    # will be needed to make "--marker" work for nested_depth lists
    events.sort(key=lambda x: x.event_time)

    # Slice the list if marker is specified
    if marker:
        try:
            marker_index = [e.id for e in events].index(marker)
            events = events[marker_index:]
        except ValueError:
            pass

    # Slice the list if limit is specified
    if limit:
        limit_index = min(int(limit), len(events))
        events = events[:limit_index]
    return events


def _get_nested_ids(hc, stack_id):
    nested_ids = []
    try:
        resources = hc.resources.list(stack_id=stack_id)
    except exc.HTTPNotFound:
        raise exc.CommandError('Stack not found: %s' % stack_id)
    for r in resources:
        nested_id = utils.resource_nested_identifier(r)
        if nested_id:
            nested_ids.append(nested_id)
    return nested_ids


def _get_nested_events(hc, nested_depth, stack_id, event_args):
    # FIXME(shardy): this is very inefficient, we should add nested_depth to
    # the event_list API in a future heat version, but this will be required
    # until kilo heat is EOL.
    nested_ids = _get_nested_ids(hc, stack_id)
    nested_events = []
    for n_id in nested_ids:
        stack_events = _get_stack_events(hc, n_id, event_args)
        if stack_events:
            nested_events.extend(stack_events)
        if nested_depth > 1:
            next_depth = nested_depth - 1
            nested_events.extend(_get_nested_events(
                hc, next_depth, n_id, event_args))
    return nested_events


def _get_stack_events(hc, stack_id, event_args):
    event_args['stack_id'] = stack_id
    try:
        events = hc.events.list(**event_args)
    except exc.HTTPNotFound as ex:
        # it could be the stack or resource that is not found
        # just use the message that the server sent us.
        raise exc.CommandError(str(ex))
    else:
        # Show which stack the event comes from (for nested events)
        for e in events:
            e.stack_name = stack_id.split("/")[0]
        return events


def poll_for_events(hc, stack_name, action=None, poll_period=5, marker=None,
                    nested_depth=0):
    """Continuously poll events and logs for performed action on stack."""

    if action:
        stop_status = ('%s_FAILED' % action, '%s_COMPLETE' % action)
        stop_check = lambda a: a in stop_status
    else:
        stop_check = lambda a: a.endswith('_COMPLETE') or a.endswith('_FAILED')

    no_event_polls = 0
    msg_template = "\n Stack %(name)s %(status)s \n"

    def is_stack_event(event):
        if getattr(event, 'resource_name', '') != stack_name:
            return False

        phys_id = getattr(event, 'physical_resource_id', '')
        links = dict((l.get('rel'),
                      l.get('href')) for l in getattr(event, 'links', []))
        stack_id = links.get('stack', phys_id).rsplit('/', 1)[-1]
        return stack_id == phys_id

    while True:
        events = get_events(hc, stack_id=stack_name, nested_depth=nested_depth,
                            event_args={'sort_dir': 'asc',
                                        'marker': marker})

        if len(events) == 0:
            no_event_polls += 1
        else:
            no_event_polls = 0
            # set marker to last event that was received.
            marker = getattr(events[-1], 'id', None)

            for event in events:
                # check if stack event was also received
                if is_stack_event(event):
                    stack_status = getattr(event, 'resource_status', '')
                    msg = msg_template % dict(
                        name=stack_name, status=stack_status)
                    if stop_check(stack_status):
                        return stack_status, msg

        if no_event_polls >= 2:
            # after 2 polls with no events, fall back to a stack get
            stack = hc.stacks.get(stack_name, resolve_outputs=False)
            stack_status = stack.stack_status
            msg = msg_template % dict(
                name=stack_name, status=stack_status)
            if stop_check(stack_status):
                return stack_status, msg
            # go back to event polling again
            no_event_polls = 0

        time.sleep(poll_period)
