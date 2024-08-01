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

from typing import Optional, TYPE_CHECKING

from .stream import Stream

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types import (
        Stream as StreamPayload,
        DataCreateStream,
        InviteInformation as InvitePayload,
    )


class Invite:
    """Represents a Lightspeed invite.

    Attributes
    ----------
    code: :class:`str`
        The invite code.
    used: :class:`bool`
        Whether the invite was used by someone.
    claimed_by: Optional[:class:`str`]
        The user that claimed this invite.
    """

    __slots__ = (
        '_state',
        'code',
        'used',
        'claimed_by',
    )

    def __init__(self, *, data: InvitePayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.code: str = data.get('id')
        self.used: bool = data['used']
        self.claimed_by: Optional[str] = data.get('claimed_by')

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} code={self.code!r} used={self.used!r} claimed_by={self.claimed_by!r}>'

    async def delete(self) -> None:
        """|coro|

        Deletes the invite.
        """
        await self._state.http.delete_stream_invite(self.code)

    async def use(self) -> Stream:
        """|coro|

        Uses a invite.

        Returns
        -------
        :class:`Stream`
            The created stream.
        """
        payload: DataCreateStream = {'invite': self.code}

        state = self._state
        data: StreamPayload = await state.http.create_stream(payload)

        return Stream(data=data, state=state)


__all__ = ('Invite',)
