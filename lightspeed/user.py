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
from typing import List, Optional, TYPE_CHECKING

from .utils import MISSING, parse_time

if TYPE_CHECKING:
    from .state import ConnectionState
    from .stream import LargeStream
    from .types import (
        User as UserPayload,
        SocialLink as SocialLinkPayload,
        DataEditUser,
        BanInformation as BanInformationPayload,
        UserInformation as UserInformationPayload,
        DataReportContent,
    )

    from typing_extensions import Self


class SocialLink:
    """A social link.

    Attributes
    ----------
    title: :class:`str`
        The social service title.
    link: :class:`str`
        The social service link URL.
    """

    __slots__ = ('title', 'link')

    def __init__(self, title: str, link: str) -> None:
        self.title = title
        self.link = link

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} title={self.title!r} link={self.link!r}>'

    @classmethod
    def from_dict(cls, data: SocialLinkPayload) -> Self:
        return cls(title=data['title'], link=data['link'])

    def to_dict(self) -> SocialLinkPayload:
        return {
            'title': self.title,
            'link': self.link,
        }


class PartialUser:
    """Represents a partial user.

    This is minimal information to display user in chat or similar location.

    Attributes
    ----------
    id: :class:`str`
        The user's ID.
    path: :class:`str`
        The path at which this user is accessible.
    name: :class:`str`
        The user's name (case-sensitive).
    avatar_id: Optional[:class:`str`]
        The user avatar's ID.
    accent_color: Optional[:class:`str`]
        The user's accent color.
    """

    __slots__ = (
        '_state',
        'id',
        'path',
        'name',
        'avatar_id',
        'accent_color',
    )

    def __init__(self, *, data: UserInformationPayload, state: ConnectionState, id: str = MISSING) -> None:
        self._state: ConnectionState = state
        self.id: str = data.get('id', data.get('_id', id))
        self.path: str = data['path']
        self.name: str = data['username']
        self.avatar_id: Optional[str] = data.get('avatar')
        self.accent_color: Optional[str] = data.get('accent_colour')

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} path={self.path!r} name={self.name!r} avatar_id={self.avatar_id!r} accent_color={self.accent_color!r}>'

    async def edit(
        self,
        *,
        name: str = MISSING,
        avatar: Optional[str] = MISSING,
        banner: Optional[str] = MISSING,
        bio: Optional[str] = MISSING,
        social_links: List[SocialLink] = MISSING,
        hidden: Optional[bool] = MISSING,
        chat_restricted: Optional[bool] = MISSING,
    ) -> User:
        """|coro|

        Edits the user.

        .. warning::
            This is available only if you're authenticated as site administrator.

        Parameters
        ----------
        name: :class:`str`
            The new username you wish to change to.
        avatar: Optional[:class:`str`]
            The new avatar's ID. Pass ``None`` to remove avatar.
        banner: Optional[:class:`str`]
            The new banner's ID. Pass ``None`` to remove banner.
        bio: Optional[:class:`str`]
            The user's description. Could be ``None`` to represent no bio.
        social_links: Optional[List[:class:`SocialLink`]]
            The new user's social links.
        hidden: Optional[:class:`bool`]
            To hide the user and their streams from public discovery or not.
        chat_restricted: Optional[:class:`bool`]
            To globally chat mute or not.

        Returns
        -------
        :class:`User`
            The newly updated user.
        """
        payload: DataEditUser = {}

        if name is not MISSING:
            payload['username'] = name

        if avatar is not MISSING:
            payload['avatar'] = avatar

        if banner is not MISSING:
            payload['banner'] = banner

        if bio is not MISSING:
            payload['bio'] = bio

        if social_links is not MISSING:
            payload['social_links'] = [sl.to_dict() for sl in social_links]

        if hidden is not MISSING:
            payload['hidden'] = hidden

        if chat_restricted is not MISSING:
            payload['chat_restricted'] = chat_restricted

        state = self._state
        data = await state.http.edit_user_as_admin(self.id, payload)
        return User(data=data, state=state)

    async def fetch(self) -> User:
        """|coro|

        Retrieves the user data.

        Returns
        -------
        :class:`User`
            The newly updated user.
        """
        state = self._state

        data = await state.http.get_user(self.path)
        return User(data=data, state=state)

    async def report(self, *, reason: str) -> None:
        """|coro|

        Reports this user to Lightspeed.tv staff.

        Parameters
        ----------
        reason: :class:`str`
            The reporting reason.
        """

        payload: DataReportContent = {
            'content': {
                'type': 'User',
                'id': self.id,
            },
            'reason': reason,
        }
        await self._state.http.report(payload)

    async def stream(self) -> LargeStream:
        """|coro|

        Retrieves a stream of this user.

        Returns
        -------
        :class:`LargeStream`
            The retrieved stream.
        """

        from .stream import LargeStream

        state = self._state
        data = await state.http.get_stream(self.path)

        return LargeStream(data=data, state=state)


class User(PartialUser):
    """Represents a Lightspeed.tv user.

    Attributes
    ----------
    id: :class:`str`
        The user's ID.
    path: :class:`str`
        The path at which this user is accessible.
    name: :class:`str`
        The user's name (case-sensitive).
    avatar_id: Optional[:class:`str`]
        The user avatar's ID.
    banner_id: Optional[:class:`str`]
        The user banner's ID.
    social_links: List[:class:`SocialLink`]
        The user social links.
    accent_color: Optional[:class:`str`]
        The user's accent color.
    privileged: :class:`bool`
        Whether the user is privileged or not.
    hidden: :class:`bool`
        Whether the user and their streams are hidden from public discovery.
    chat_restricted: :class:`bool`
        Whether the user is globally chat-muted.
    following: List[:class:`User`]
        The users that this user is following.
    following_ids: List[:class:`str`]
        The IDs of users that this user is following.
    """

    __slots__ = (
        '_state',
        'id',
        'path',
        'name',
        'avatar_id',
        'banner_id',
        'social_links',
        'accent_color',
        'privileged',
        'hidden',
        'chat_restricted',
        'following',
        'following_ids',
    )

    def __init__(self, *, data: UserPayload, state: ConnectionState, id: str = MISSING) -> None:
        # UserInformationPayload has `id`, but UserPayload has `_id`. The constructor actually accepts both.
        super().__init__(data=data, state=state, id=id)  # type: ignore
        self.banner_id: Optional[str] = data.get('banner')

        social_links = data.get('social_links')
        if social_links:
            self.social_links: List[SocialLink] = [SocialLink.from_dict(sl) for sl in social_links]
        else:
            self.social_links = []

        self.privileged: bool = data.get('privileged') or False
        self.hidden: bool = data.get('hidden') or False
        self.chat_restricted: bool = data.get('chat_restricted') or False

        self.following: List[User] = [User(data=f, state=state) for f in data.get('following') or []]
        self.following_ids: List[str] = data.get('following_ids') or []

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} path={self.path!r} name={self.name!r} avatar_id={self.avatar_id!r} banner_id={self.banner_id!r} social_links={self.social_links!r} accent_color={self.accent_color!r} privileged={self.privileged!r} hidden={self.hidden!r} chat_restricted={self.chat_restricted!r} following={self.following!r} following_ids={self.following_ids}>'


class UserBan:
    """Represents a ban on Lightspeed.tv stream.

    Attributes
    ----------
    stream_id: :class:`str`
        The stream ID where you're banned.
    expires_at: Optional[:class:`datetime.datetime`]
        When the ban will expire. This is ``None`` for permament bans.
    """

    __slots__ = ('stream_id', 'expires_at')

    def __init__(self, *, data: BanInformationPayload) -> None:
        self.stream_id: Optional[str] = data['stream_id']
        self.expires_at: Optional[datetime.datetime] = parse_time(data.get('expires'))

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} stream_id={self.stream_id!r} expires_at={self.expires_at!r}>'


class ClientUser(User):
    async def bans(self) -> List[UserBan]:
        """|coro|

        Retrieves your own stream bans.

        Returns
        -------
        List[:class:`UserBan`]
            The retrieved bans.
        """
        bans = await self._state.http.my_bans()
        return [UserBan(data=b) for b in bans]

    async def edit(
        self,
        *,
        name: str = MISSING,
        avatar: Optional[str] = MISSING,
        banner: Optional[str] = MISSING,
        bio: Optional[str] = MISSING,
        social_links: Optional[List[SocialLink]] = MISSING,
        hidden: Optional[bool] = MISSING,
        chat_restricted: Optional[bool] = MISSING,
    ) -> User:
        """|coro|

        Edits the current user.

        Parameters
        ----------
        name: :class:`str`
            The new username you wish to change to.
        avatar: Optional[:class:`str`]
            The new avatar's ID. Pass ``None`` to remove avatar.
        banner: Optional[:class:`str`]
            The new banner's ID. Pass ``None`` to remove banner.
        bio: Optional[:class:`str`]
            The user's description. Could be ``None`` to represent no bio.
        social_links: Optional[List[:class:`SocialLink`]]
            The new user's social links.
        hidden: Optional[:class:`bool`]
            To hide the user and their streams from public discovery or not.
        chat_restricted: Optional[:class:`bool`]
            To globally chat mute or not.

        Returns
        -------
        :class:`ClientUser`
            The newly updated user.
        """
        payload: DataEditUser = {}

        if name is not MISSING:
            payload['username'] = name

        if avatar is not MISSING:
            payload['avatar'] = avatar

        if banner is not MISSING:
            payload['banner'] = banner

        if bio is not MISSING:
            payload['bio'] = bio

        if social_links is not MISSING:
            if social_links is None:
                payload['social_links'] = None
            else:
                payload['social_links'] = [sl.to_dict() for sl in social_links]

        if hidden is not MISSING:
            payload['hidden'] = hidden

        if chat_restricted is not MISSING:
            payload['chat_restricted'] = chat_restricted

        state = self._state
        data = await state.http.edit_my_user(payload)
        return User(data=data, state=state)


__all__ = (
    'SocialLink',
    'PartialUser',
    'User',
    'UserBan',
    'ClientUser',
)
