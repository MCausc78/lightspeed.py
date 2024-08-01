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

from typing import TYPE_CHECKING, Union

from .user import PartialUser

if TYPE_CHECKING:
    import lightspeed.abc
    from .types import Message as MessagePayload


class PartialMessage:
    """Represents partial message in a Lightspeed.tv chat.

    Attributes
    ----------
    id: :class:`str`
        The message's ID.
    chat: Union[:class:`PartialStream`, :class:`Stream`, :class:`LargeStream`]
        The chat that this message was sent in.
    """

    __slots__ = (
        'id',
        'chat',
    )

    def __init__(self, *, id: str, chat: lightspeed.abc.MessageableChat) -> None:
        self.id: str = id
        self.chat: lightspeed.abc.MessageableChat = chat

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id}>'

    async def delete(self) -> None:
        """|coro|

        Deletes the message.
        """
        chat = await self.chat._get_chat()
        await chat._state.http.delete_chat_message(chat.id, self.id)


class Message(PartialMessage):
    """Represents message in a Lightspeed.tv chat.

    Attributes
    ----------
    stream_id: :class:`str`
        The stream's ID.
    author: :class:`PartialUser`
        The message author.
    author_id: :class:`str`
        The message author's ID.
    content: :class:`str`
        The message content.
    """

    __slots__ = (
        '_chat',
        'id',
        'stream_id',
        'author',
        'author_id',
        'content',
    )

    def __init__(self, *, data: MessagePayload, chat: lightspeed.abc.MessageableChat) -> None:
        super().__init__(id=data['_id'], chat=chat)

        state = chat._state
        self.author: PartialUser = PartialUser(data=data['author'], state=state)
        self.author_id: str = data['author_id']
        self.content: str = data['content']

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id} stream_id={self.stream_id!r} author={self.author!r} author_id={self.author_id!r} content={self.content!r}>'


__all__ = ('PartialMessage', 'Message')
