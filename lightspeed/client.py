"""
The MIT License (MIT)

Copyright (c) 2024-present MCausc78

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import aiohttp
import logging
from typing import AsyncIterator, List, Optional, TYPE_CHECKING, Type

from .category import Category
from .http import HTTPClient
from .invite import Invite
from .region import Region
from .state import ConnectionState
from .stream import Stream, LargeStream
from .user import User, ClientUser
from .utils import MISSING

if TYPE_CHECKING:
    from .types import (
        DataCreateStream,
        DataEditStream,
        DataCreateUser,
        DataCreateCategory,
        DataCreateInvite,
        InviteInformation as InvitePayload,
    )

    from types import TracebackType
    from typing_extensions import Self

_log = logging.getLogger(__name__)


class Client:
    r"""Represents a client connection that connects to Lightspeed.
    This class is used to interact with the Lightspeed API.

    .. container:: operations

        .. describe:: async with x

            Asynchronously initialises the client and automatically cleans up.
    """

    __slots__ = (
        '_connection',
        'http',
    )

    def __init__(
        self,
        *,
        http_base: str = MISSING,
        connector: Optional[aiohttp.BaseConnector] = None,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        http_trace: Optional[aiohttp.TraceConfig] = None,
    ) -> None:
        self.http: HTTPClient = HTTPClient(
            connector=connector,
            base=http_base,
            proxy=proxy,
            proxy_auth=proxy_auth,
            http_trace=http_trace,
        )
        self._connection = self._get_state()

    def _get_state(self) -> ConnectionState:
        return ConnectionState(http=self.http)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    # login state management

    @property
    def user(self) -> Optional[ClientUser]:
        """Optional[:class:`ClientUser`]: Represents the connected client. ``None`` if not logged in."""

    async def login(self, token: Optional[str] = None) -> None:
        """|coro|

        Logs in the client with the specified credentials.


        Parameters
        -----------
        token: Optional[:class:`str`]
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.

        Raises
        ------
        LoginFailure
            The wrong credentials are passed.
        HTTPException
            An unknown HTTP related error occurred,
            usually when it isn't 200 or the known incorrect credentials
            passing status code.
        """

        _log.info('logging in using static token')

        if token is not None:
            if not isinstance(token, str):
                raise TypeError(f'expected token to be a str, received {token.__class__.__name__} instead')
            token = token.strip()
            data = await self.http.static_login(token)
            self._connection.user = ClientUser(state=self._connection, data=data)
        else:
            await self.http.startup()

    async def close(self) -> None:
        """|coro|

        Closes the connection to Lightspeed.
        """
        await self.http.close()

    async def fetch_regions(self) -> List[Region]:
        """|coro|

        Retrieves all streaming regions.

        Returns
        -------
        List[:class:`Region`]
            The retrieved regions.
        """
        state = self._connection

        data = await self.http.get_regions()
        return [Region(data=d, state=state) for d in data]

    async def fetch_streams(self, *, admin: bool = False) -> AsyncIterator[Stream]:
        """|coro|

        Retrieves streams on home page.

        Parameters
        ----------
        admin: :class:`bool`
            Whether to fetch hidden streams or not.

            .. warning::
                This is available only if you're authenticated as site administrator.


        Yields
        ------
        List[:class:`Stream`]
            The retrieved stream.
        """
        state = self._connection

        if admin:
            data = await self.http.get_streams_as_admin()
        else:
            data = await self.http.get_streams()

        for d in data:
            yield LargeStream(data=d, state=state)

    async def create_stream(self, code: str, /) -> Stream:
        """|coro|

        Enable streaming on a user account.

        Parameters
        ----------
        code: :class:`str`
            The invite code, given by Lightspeed.tv team.

        Returns
        -------
        :class:`Stream`
            The created stream.
        """
        payload: DataCreateStream = {'invite': code}

        state = self._connection
        data = await self.http.create_stream(payload)

        return Stream(data=data, state=state)

    async def fetch_my_stream(self) -> Stream:
        """|coro|

        Retrieves your stream.

        Returns
        -------
        :class:`Stream`
            The retrieved stream.
        """
        state = self._connection
        data = await self.http.my_stream()

        return Stream(data=data, state=state)

    async def edit_my_stream(
        self,
        *,
        title: str = MISSING,
        description: str = MISSING,
        thumbnail: Optional[str] = MISSING,
        tags: List[str] = MISSING,
        category: str = MISSING,
        rtmp_relay: str = MISSING,
    ) -> Stream:
        """|coro|

        Edits your stream.

        Parameters
        ----------
        title: :class:`str`
            The new stream title.
        description: :class:`str`
            The new stream's description.
        thumbnail: Optional[:class:`str`]
            The new stream's thumbnail. Could be ``None`` to denote no thumbnail.
        tags: List[:class:`str`]
            The new stream tags.
        category: :class:`str`
            The category to move this stream into.
        rtmp_relay: :class:`str`
            The RTMP URL to relay the stream to.

        Returns
        -------
        :class:`Stream`
            The newly updated stream.
        """
        payload: DataEditStream = {}

        if title is not MISSING:
            payload['title'] = title

        if description is not MISSING:
            payload['description'] = description

        if thumbnail is not MISSING:
            payload['thumbnail'] = thumbnail

        if tags is not MISSING:
            payload['tags'] = tags

        if category is not MISSING:
            payload['category'] = category

        if rtmp_relay is not MISSING:
            payload['rtmp_relay'] = rtmp_relay

        state = self._connection
        data = await self.http.edit_my_stream(payload)
        return Stream(data=data, state=state)

    async def fetch_stream(self, path: str, /) -> LargeStream:
        """|coro|

        Retrieves a stream by user path.

        Parameters
        ----------
        path: :class:`str`
            The user path.

        Returns
        -------
        :class:`LargeStream`
            The retrieved stream.
        """
        state = self._connection
        data = await self.http.get_stream(path)

        return LargeStream(data=data, state=state)

    async def reset_stream_token(self) -> Stream:
        """|coro|

        Resets the token used for this account's stream.

        Returns
        -------
        :class:`Stream`
            The updated stream with new token.
        """
        state = self._connection
        data = await self.http.reset_stream_token()

        return Stream(data=data, state=state)

    async def fetch_my_user(self) -> ClientUser:
        """|coro|

        Retrieves current authenticated user.

        Returns
        -------
        :class:`ClientUser`
            The retrieved client user.
        """
        state = self._connection

        data = await self.http.get_me()
        return ClientUser(data=data, state=state)

    async def create_user(self, name: str, /) -> ClientUser:
        """|coro|

        Sets up user name and allows user to continue using Lightspeed.

        Returns
        -------
        :class:`ClientUser`
            The newly created client user.
        """
        state = self._connection

        payload: DataCreateUser = {'username': name}
        data = await self.http.create_user(payload)
        return ClientUser(data=data, state=state)

    async def fetch_user(self, path: str, /) -> User:
        """|coro|

        Retrieves a user by user path.

        Parameters
        ----------
        path: :class:`str`
            The user path.

        Returns
        -------
        :class:`User`
            The retrieved user.
        """
        state = self._connection
        data = await self.http.get_user(path)

        return User(data=data, state=state)

    async def create_category(self, title: str, *, cover_image: Optional[str] = None, description: str) -> Category:
        """|coro|

        Creates a category.

        Parameters
        ----------
        title: :class:`str`
            The category title.
        cover_image: Optional[:class:`str`]
            The cover image attachment ID.
        description: :class:`str`
            The category description.

        Returns
        -------
        :class:`Category`
            The created category.
        """
        payload: DataCreateCategory = {
            'title': title,
            'cover': cover_image,
            'description': description,
        }

        data = await self.http.create_category(payload)
        state = self._connection

        return Category(data=data, state=state)

    async def categories(self) -> AsyncIterator[Category]:
        """|coro|

        Retrieves all available streaming categories.

        Yields
        ------
        :class:`Category`
            The category.
        """
        data = await self.http.list_categories()
        state = self._connection

        for d in data:
            yield Category(data=d, state=state)

    async def invites(self) -> AsyncIterator[Invite]:
        """|coro|

        Retrieves all invites.

        Yields
        ------
        :class:`Invite`
            The invite.
        """
        data = await self.http.list_stream_invites()
        state = self._connection

        for d in data:
            yield Invite(data=d, state=state)

    async def create_invite(self, code: str) -> Invite:
        """|coro|

        Creates a invite.

        Returns
        -------
        :class:`Invite`
            The created invite.
        """
        payload: DataCreateInvite = {'code': code}

        await self.http.create_stream_invite(payload)
        state = self._connection

        data: InvitePayload = {
            'id': code,
            'used': False,
            'claimed_by': None,
        }
        return Invite(data=data, state=state)
