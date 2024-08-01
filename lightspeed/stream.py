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

import datetime

from typing import AsyncIterator, List, Optional, TYPE_CHECKING

from .abc import Messageable, Identifier
from .category import Category
from .enums import Controller
from .message import PartialMessage
from .mixins import EqualityComparable
from .region import Region
from .user import User
from .utils import MISSING, parse_time

if TYPE_CHECKING:
    from .abc import MessageableChat
    from .state import ConnectionState
    from .types import (
        Stream as StreamPayload,
        Live as LivePayload,
        DataEditStream,
        AggregateStream as AggregateStreamPayload,
        Ban as BanPayload,
        DataBanUser,
        DataReportContent,
    )


class Ban:
    """Represents a ban on Lightspeed stream.

    Attributes
    ----------
    id: :class:`str`
        The ban case' ID.
    stream_id: :class:`str`
        The stream ID where this ban was given at.
    user_id: :class:`str`
        The banned user's ID.
    mod_id: :class:`str`
        The moderator ID.
    reason: Optional[:class:`str`]
        The reason of the ban.
    expires_at: Optional[:class:`datetime.datetime`]
        When the ban expires.
    user: Optional[:class:`User`]
        The user that was banned.
    """

    __slots__ = (
        '_state',
        'id',
        'stream_id',
        'user_id',
        'mod_id',
        'reason',
        'expires_at',
        'user',
    )

    def __init__(self, *, data: BanPayload, state: ConnectionState, user: Optional[User]) -> None:
        self._state = state

        self.id: str = data['_id']
        self.stream_id: str = data['stream_id']
        self.user_id: str = data['user_id']
        self.mod_id: str = data['mod_id']
        self.reason: Optional[str] = data.get('reason')

        expires = data.get('expires')
        if expires:
            self.expires_at: Optional[datetime.datetime] = datetime.datetime.fromisoformat(expires)
        else:
            self.expires_at = None
        self.user: Optional[User] = user

    async def remove(self) -> None:
        """|coro|

        Removes the ban from the stream. Equivalent to :meth:`PartialStream.unban` call.
        """
        await self._state.http.unban(self.stream_id, self.user_id)


class PartialStream(EqualityComparable, Messageable):
    """Represents a partial stream on Lightspeed.

    Attributes
    ----------
    id: :class:`str`
        The stream's ID.
    """

    __slots__ = (
        '_state',
        'id',
    )

    def __init__(self, *, id: str, state: ConnectionState) -> None:
        self._state = state
        self.id = id

    async def _get_chat(self) -> MessageableChat:
        return self

    def get_partial_message(self, message_id: str, /) -> PartialMessage:
        """Creates a PartialMessage from the message ID.

        This is useful if you want to work with a message and only have its ID without doing an unnecessary API call.

        Returns
        -------
        :class:`PartialMessage`
            The partial message.
        """
        return PartialMessage(id=message_id, chat=self)

    async def ban(self, user: Identifier, until: Optional[datetime.datetime] = None) -> Ban:
        """|coro|

        Bans a user from the stream.

        Parameters
        ----------
        user: :class:`Identifier`
            The user to ban from the stream.
        until: Optional[:class:`datetime.datetime`]
            When the ban expires.

        Returns
        -------
        :class:`Ban`
            The ban.
        """
        payload: DataBanUser = {}

        if until not in (None, MISSING):
            payload['expires'] = until.isoformat()

        state = self._state
        data = await state.http.ban(self.id, user.id, payload)
        return Ban(data=data, state=state, user=None)

    async def bans(self) -> AsyncIterator[Ban]:
        """|coro|

        Lists all bans of the stream.

        Yields
        ------
        :class:`Ban`
            The ban.
        """
        state = self._state

        resp = await state.http.get_stream_bans(self.id)

        users = {u['_id']: User(data=u, state=state) for u in resp['users']}
        for data in resp['bans']:
            ban = Ban(data=data, state=state, user=None)
            ban.user = users[ban.user_id]
            yield ban

    async def demote(self, user: Identifier) -> None:
        """|coro|

        Demotes a user from stream moderator.

        Parameters
        ----------
        user: :class:`Identifier`
            The user to demote from moderator.
        """
        await self._state.http.demote(self.id, user.id)

    async def edit(
        self,
        *,
        title: str = MISSING,
        description: str = MISSING,
        thumbnail: Optional[str] = MISSING,
        tags: List[str] = MISSING,
        category: str = MISSING,
        rtmp_relay: str = MISSING,
        suspended: bool = MISSING,
    ) -> Stream:
        """|coro|

        Edits the stream.

        .. warning::
            This is available only if you're authenticated as site administrator.

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
        suspended: :class:`bool`
            To suspend the stream or not.

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

        if suspended is not MISSING:
            payload['suspended'] = suspended

        state = self._state
        data = await state.http.edit_stream_as_admin(self.id, payload)
        return Stream(data=data, state=state, id=self.id)

    async def fetch_mods(self) -> List[User]:
        """|coro|

        Lists all moderators of the stream.

        Returns
        ------
        List[:class:`User`]
            The stream moderators.
        """
        state = self._state

        mods = await state.http.get_stream_moderators(self.id)
        return [User(data=u, state=state) for u in mods]

    async def follow(self) -> None:
        """|coro|

        Follows the stream.
        """
        await self._state.http.follow_stream(self.id)

    async def promote(self, user: Identifier) -> None:
        """|coro|

        Promotes a user to stream moderator.

        Parameters
        ----------
        user: :class:`Identifier`
            The user to promote.
        """
        await self._state.http.promote(self.id, user.id)

    async def stop(self) -> Stream:
        """|coro|

        Disconnects all users from a stream and stop it.

        .. warning::
            This is available only if you're authenticated as site administrator.
        """

        state = self._state
        data = await state.http.stop_stream_as_admin(self.id)
        return Stream(data=data, state=state, id=self.id)

    async def unban(self, user: Identifier) -> None:
        """|coro|

        Unbans a user from the stream.

        Parameters
        ----------
        user: :class:`Identifier`
            The user to unban from the stream.
        """
        await self._state.http.unban(self.id, user.id)

    async def unfollow(self) -> None:
        """|coro|

        Unfollows the stream.
        """
        await self._state.http.unfollow_stream(self.id)


class Live:
    """Represents bit of information about active stream.

    Attributes
    ----------
    started_at: :class:`datetime.datetime`
        When the stream started.
    region: :class:`str`
        The region that you should use when connecting in order to watch.
    controller: Optional[:class:`Controller`]
        A way how you should connect to this live stream.
    """

    __slots__ = (
        'started_at',
        'region',
        'controller',
    )

    def __init__(self, *, data: LivePayload) -> None:
        self.started_at: datetime.datetime = parse_time(data['started_at'])
        self.region: str = data['region']

        controller = data.get('controller')
        if controller:
            self.controller: Optional[Controller] = Controller(controller)
        else:
            self.controller = None


class Stream(PartialStream):
    """Represents a stream on Lightspeed.

    Attributes
    ----------
    id: :class:`str`
        The stream's ID.
    ftl_id: Optional[:class:`int`]
        The ID used for FTL protocol.
    title: :class:`str`
        The stream title. This is usually filled in.
    description: :class:`str`
        The stream description.
    thumbnail_id: Optional[:class:`str`]
        The stream thumbnail ID.
    tags: List[:class:`str`]
        The stream tags.
    token: :class:`str`
        The FTL token. This can be empty in some cases.
    live: Optional[:class:`Live`]
        The information about active stream, if it is live.
    category_id: :class:`str`
        The ID of the stream category.
    moderators: List[:class:`str`]
        The IDs of stream moderators.
    record_vod: :class:`bool`
        Whether to record VODs for this stream or not.
    suspended: :class:`bool`
        Whether the stream is currently prohibited from going live.
    rtmp_relay: Optional[:class:`str`]
        The RTMP URL to relay the stream to.
    last_streamed_at: Optional[:class:`datetime.datetime`]
        When the stream was ended last time.
    """

    __slots__ = (
        '_state',
        'id',
        'ftl_id',
        'title',
        'description',
        'thumbnail_id',
        'tags',
        'token',
        'live',
        'category_id',
        'moderators',
        'record_vod',
        'suspended',
        'rtmp_relay',
        'last_streamed_at',
    )

    def __init__(self, *, data: StreamPayload, state: ConnectionState, id: str = MISSING) -> None:
        self._state = state
        self.id: str = data.get('_id', id)
        self.ftl_id: Optional[int] = data.get('ftl_id')

        try:
            self.title: str = data['title']
        except KeyError:
            self.title = ''

        self.description: str = data.get('description', '')
        self.thumbnail_id: Optional[str] = data.get('thumbnail')
        self.category_id: str = data.get('category', 'default')
        self.moderators: List[str] = data.get('moderators', [])
        self.tags: List[str] = data.get('tags', [])
        self.token: str = data.get('token') or ''

        live = data.get('live')
        if live:
            self.live: Optional[Live] = Live(data=live)
        else:
            self.live = None
        self.record_vod: bool = data.get('record', True)
        self.suspended: bool = data.get('suspended', False)
        self.rtmp_relay: Optional[str] = data.get('rtmp_relay')
        self.last_streamed_at: Optional[datetime.datetime] = parse_time(data.get('last_streamed'))

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} ftl_id={self.ftl_id!r} title={self.title!r} description={self.description!r} tags={self.tags!r} token={self.token!r} live={self.live!r} category_id={self.category_id!r} moderators={self.moderators!r} record_vod={self.record_vod!r} suspended={self.suspended!r} rtmp_relay={self.rtmp_relay} last_streamed_at={self.last_streamed_at!r}>'


class LargeStream(Stream):
    """Represents a large stream on Lightspeed.

    This class derives from :class:`Stream` in order to provide more attributes.

    Attributes
    ----------
    user: :class:`User`
        The user that this stream belongs to.

        .. note::
            :attr:`User.id` will be empty due to Lightspeed limitation.
    category: :class:`Category`
        The category.
    region: Optional[:class:`Region`]
        The region this stream is currently live in.
    follower_count: :class:`int`
        The count of followers that this stream has.
    """

    __slots__ = (
        '_state',
        'id',
        'ftl_id',
        'title',
        'description',
        'thumbnail_id',
        'tags',
        'token',
        'live',
        'category_id',
        'moderators',
        'record_vod',
        'suspended',
        'rtmp_relay',
        'last_streamed_at',
        'user',
        'category',
        'region',
        'follower_count',
    )

    def __init__(self, *, data: AggregateStreamPayload, state: ConnectionState) -> None:
        super().__init__(
            data=data['stream'],
            state=state,
            id=data['_id'],
        )
        self.user: User = User(data=data['user'], state=state, id='')
        self.category: Category = Category(data=data['category'], state=state)

        region = data.get('region')
        if region:
            self.region: Optional[Region] = Region(data=region, state=state)
        else:
            self.region = None
        self.follower_count = data.get('follower_count') or 0

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} ftl_id={self.ftl_id!r} title={self.title!r} description={self.description!r} tags={self.tags!r} token={self.token!r} live={self.live!r} category_id={self.category_id!r} moderators={self.moderators!r} record_vod={self.record_vod!r} suspended={self.suspended!r} rtmp_relay={self.rtmp_relay} last_streamed_at={self.last_streamed_at!r} user={self.user!r} category={self.category!r} region={self.region!r} follower_count={self.follower_count!r}>'

    async def report(self, *, reason: str) -> None:
        """|coro|

        Reports this stream to Lightspeed.tv staff.

        Parameters
        ----------
        reason: :class:`str`
            The reporting reason.
        """

        payload: DataReportContent = {
            'content': {
                'type': 'Stream',
                'path': self.user.path,
            },
            'reason': reason,
        }
        await self._state.http.report(payload)


__all__ = (
    'Ban',
    'PartialStream',
    'Live',
    'Stream',
    'LargeStream',
)
