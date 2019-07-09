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
import six

from openstack import exceptions
from openstack import resource


class Resource(resource.Resource):

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
        :raises: :class:`openstack.exceptions.ResourceNotFound` if nothing
                 is found and ignore_missing is ``False``.
        """
        session = cls._get_session(session)
        # Try to short-circuit by looking directly for a matching ID.
        try:
            match = cls.existing(
                id=name_or_id,
                connection=session._get_connection(),
                **params)
            return match.fetch(session, **params)
        except exceptions.SDKException:
            # DNS may return 400 when we try to do GET with name
            pass

        if ('name' in cls._query_mapping._mapping.keys()
                and 'name' not in params):
            params['name'] = name_or_id

        data = cls.list(session, **params)

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.ResourceNotFound(
            "No %s found for %s" % (cls.__name__, name_or_id))

    @classmethod
    def _get_next_link(cls, uri, response, data, marker, limit, total_yielded):
        next_link = None
        params = {}
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
            parts = six.moves.urllib.parse.urlparse(next_link)
            query_params = six.moves.urllib.parse.parse_qs(parts.query)
            params.update(query_params)
            next_link = six.moves.urllib.parse.urljoin(next_link,
                                                       parts.path)

        # If we still have no link, and limit was given and is non-zero,
        # and the number of records yielded equals the limit, then the user
        # is playing pagination ball so we should go ahead and try once more.
        if not next_link and limit:
            next_link = uri
            params['marker'] = marker
            params['limit'] = limit
        return next_link, params
