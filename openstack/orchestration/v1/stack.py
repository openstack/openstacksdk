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
from openstack.common import tag
from openstack import exceptions
from openstack import resource
from openstack import utils


class Stack(resource.Resource):
    name_attribute = 'stack_name'
    resource_key = 'stack'
    resources_key = 'stacks'
    base_path = '/stacks'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'action',
        'name',
        'status',
        'project_id',
        'owner_id',
        'username',
        project_id='tenant_id',
        **tag.TagMixin._tag_query_parameters,
    )

    # Properties
    #: A list of resource objects that will be added if a stack update
    #  is performed.
    added = resource.Body('added')
    #: Placeholder for AWS compatible template listing capabilities
    #: required by the stack.
    capabilities = resource.Body('capabilities')
    #: Timestamp of the stack creation.
    created_at = resource.Body('creation_time')
    #: A text description of the stack.
    description = resource.Body('description')
    #: A list of resource objects that will be deleted if a stack
    #: update is performed.
    deleted = resource.Body('deleted', type=list)
    #: Timestamp of the stack deletion.
    deleted_at = resource.Body('deletion_time')
    #: A JSON environment for the stack.
    environment = resource.Body('environment')
    #: An ordered list of names for environment files found in the files dict.
    environment_files = resource.Body('environment_files', type=list)
    #: Additional files referenced in the template or the environment
    files = resource.Body('files', type=dict)
    #: Name of the container in swift that has child
    #: templates and environment files.
    files_container = resource.Body('files_container')
    #: Whether the stack will support a rollback operation on stack
    #: create/update failures. *Type: bool*
    is_rollback_disabled = resource.Body('disable_rollback', type=bool)
    #: A list of dictionaries containing links relevant to the stack.
    links = resource.Body('links')
    #: Name of the stack.
    name = resource.Body('stack_name')
    stack_name = resource.URI('stack_name')
    #: Placeholder for future extensions where stack related events
    #: can be published.
    notification_topics = resource.Body('notification_topics')
    #: A list containing output keys and values from the stack, if any.
    outputs = resource.Body('outputs')
    #: The ID of the owner stack if any.
    owner_id = resource.Body('stack_owner')
    #: A dictionary containing the parameter names and values for the stack.
    parameters = resource.Body('parameters', type=dict)
    #: The ID of the parent stack if any
    parent_id = resource.Body('parent')
    #: A list of resource objects that will be replaced if a stack update
    #: is performed.
    replaced = resource.Body('replaced')
    #: A string representation of the stack status, e.g. ``CREATE_COMPLETE``.
    status = resource.Body('stack_status')
    #: A text explaining how the stack transits to its current status.
    status_reason = resource.Body('stack_status_reason')
    #: A list of strings used as tags on the stack
    tags = resource.Body('tags', type=list, default=[])
    #: A dict containing the template use for stack creation.
    template = resource.Body('template', type=dict)
    #: Stack template description text. Currently contains the same text
    #: as that of the ``description`` property.
    template_description = resource.Body('template_description')
    #: A string containing the URL where a stack template can be found.
    template_url = resource.Body('template_url')
    #: Stack operation timeout in minutes.
    timeout_mins = resource.Body('timeout_mins')
    #: A list of resource objects that will remain unchanged if a stack
    #: update is performed.
    unchanged = resource.Body('unchanged')
    #: A list of resource objects that will have their properties updated
    #: in place if a stack update is performed.
    updated = resource.Body('updated')
    #: Timestamp of last update on the stack.
    updated_at = resource.Body('updated_time')
    #: The ID of the user project created for this stack.
    user_project_id = resource.Body('stack_user_project_id')

    def create(self, session, prepend_key=False, *args, **kwargs):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super().create(session, prepend_key, *args, **kwargs)

    def commit(
        self,
        session,
        prepend_key=True,
        has_body=True,
        retry_on_conflict=None,
        base_path=None,
        *,
        microversion=None,
        preview=False,
        **kwargs,
    ):
        # This overrides the default behavior of resource update because
        # we need to use other endpoint for update preview.
        base_path = None
        if self.name and self.id:
            base_path = f'/stacks/{self.name}/{self.id}'
        elif self.name or self.id:
            # We have only one of name/id. Do not try to build a stacks/NAME/ID
            # path
            base_path = f'/stacks/{self.name or self.id}'
        request = self._prepare_request(
            prepend_key=False, requires_id=False, base_path=base_path
        )

        microversion = self._get_microversion(session)

        request_url = request.url
        if preview:
            request_url = utils.urljoin(request_url, 'preview')

        response = session.put(
            request_url,
            json=request.body,
            headers=request.headers,
            microversion=microversion,
        )

        self.microversion = microversion
        self._translate_response(response, has_body=True)
        return self

    def _action(self, session, body):
        """Perform stack actions"""
        url = utils.urljoin(self.base_path, self._get_id(self), 'actions')
        resp = session.post(url, json=body, microversion=self.microversion)
        exceptions.raise_from_response(resp)
        return resp

    def check(self, session):
        return self._action(session, {'check': ''})

    def abandon(self, session):
        url = utils.urljoin(
            self.base_path, self.name, self._get_id(self), 'abandon'
        )
        resp = session.delete(url)
        return resp.json()

    def export(self, session):
        """Export a stack data

        :param session: The session to use for making this request.
        :return: A dictionary containing the stack data.
        """
        url = utils.urljoin(
            self.base_path, self.name, self._get_id(self), 'export'
        )
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        return resp.json()

    def suspend(self, session):
        """Suspend a stack

        :param session: The session to use for making this request
        :returns: None
        """
        body = {"suspend": None}
        self._action(session, body)

    def resume(self, session):
        """Resume a stack

        :param session: The session to use for making this request
        :returns: None
        """
        body = {"resume": None}
        self._action(session, body)

    def fetch(
        self,
        session,
        requires_id=True,
        base_path=None,
        error_message=None,
        skip_cache=False,
        *,
        resolve_outputs=True,
        **params,
    ):
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, "fetch")

        request = self._prepare_request(
            requires_id=requires_id, base_path=base_path
        )
        # session = self._get_session(session)
        microversion = self._get_microversion(session)

        # NOTE(gtema): would be nice to simply use QueryParameters, however
        # Heat return 302 with parameters being set into URL and requests
        # apply parameters again, what results in them being set doubled
        if not resolve_outputs:
            request.url = request.url + '?resolve_outputs=False'
        response = session.get(
            request.url, microversion=microversion, skip_cache=skip_cache
        )
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self.microversion = microversion
        self._translate_response(response, **kwargs)

        if self and self.status in ['DELETE_COMPLETE', 'ADOPT_COMPLETE']:
            raise exceptions.NotFoundException(f"No stack found for {self.id}")
        return self

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.NotFoundException` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict params: Any additional parameters to be passed into
                            underlying methods, such as to
                            :meth:`~openstack.resource.Resource.existing`
                            in order to pass on URI parameters.

        :return: The :class:`Resource` object matching the given name or id
                 or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
                 than one resource is found for this request.
        :raises: :class:`openstack.exceptions.NotFoundException` if nothing
                 is found and ignore_missing is ``False``.
        """
        session = cls._get_session(session)
        # Try to short-circuit by looking directly for a matching ID.
        try:
            match = cls.existing(
                id=name_or_id, connection=session._get_connection(), **params
            )
            return match.fetch(session, **params)
        except exceptions.NotFoundException:
            pass

        # NOTE(gtema) we do not do list, since previous call has done this
        # for us already

        if ignore_missing:
            return None
        raise exceptions.NotFoundException(
            f"No {cls.__name__} found for {name_or_id}"
        )


StackPreview = Stack
