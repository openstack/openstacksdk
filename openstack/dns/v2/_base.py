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

import typing as ty
import urllib.parse

from keystoneauth1 import adapter
import typing_extensions as ty_ext

from openstack import exceptions
from openstack import resource


class Resource(resource.Resource):
    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[True] = True,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None: ...

    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[False],
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self: ...

    # excuse the duplication here: it's mypy's fault
    # https://github.com/python/mypy/issues/14764
    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None: ...

    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool = True,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None:
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
                id=name_or_id,
                connection=session._get_connection(),  # type: ignore
                **params,
            )
            return match.fetch(session)
        except exceptions.SDKException:
            # DNS may return 400 when we try to do GET with name
            pass

        if (
            'name' in cls._query_mapping._mapping.keys()
            and 'name' not in params
        ):
            params['name'] = name_or_id

        data = cls.list(
            session,
            list_base_path=list_base_path,
            microversion=microversion,
            all_projects=all_projects,
            **params,
        )

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.NotFoundException(
            f"No {cls.__name__} found for {name_or_id}"
        )

    @classmethod
    def list(
        cls,
        session: adapter.Adapter,
        paginated: bool = True,
        base_path: str | None = None,
        allow_unknown_params: bool = False,
        *,
        microversion: str | None = None,
        headers: dict[str, str] | None = None,
        max_items: int | None = None,
        project_id: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        if project_id or all_projects is not None:
            if headers is None:
                headers = {}
            if project_id:
                headers["x-auth-sudo-project-id"] = str(project_id)
            if all_projects:
                headers["x-auth-all-projects"] = str(all_projects)

        return super().list(session=session, headers=headers, **params)

    @classmethod
    def _get_next_link(cls, uri, response, data, marker, limit, total_yielded):
        next_link = None
        params: dict[str, list[str] | str] = {}
        if isinstance(data, dict):
            links = data.get('links')
            if links:
                next_link = links.get('next')

            total = data.get('metadata', {}).get('total_count')
            if total:
                # We have a kill switch
                total_count = int(total)
                if total_count <= total_yielded:
                    return None, params

        # Parse params from Link (next page URL) into params.
        # This prevents duplication of query parameters that with large
        # number of pages result in HTTP 414 error eventually.
        if next_link:
            parts = urllib.parse.urlparse(next_link)
            query_params = urllib.parse.parse_qs(parts.query)
            params.update(query_params)
            next_link = urllib.parse.urljoin(next_link, parts.path)

        # If we still have no link, and limit was given and is non-zero,
        # and the number of records yielded equals the limit, then the user
        # is playing pagination ball so we should go ahead and try once more.
        if not next_link and limit:
            next_link = uri
            params['marker'] = marker
            params['limit'] = limit

        return next_link, params
