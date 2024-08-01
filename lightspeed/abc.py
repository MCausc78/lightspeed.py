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

from abc import ABC, abstractmethod
from inspect import isawaitable
from typing import Protocol, TYPE_CHECKING, runtime_checkable

from .message import PartialMessage, Message

if TYPE_CHECKING:
    from typing import Any, AsyncIterator

    from .state import ConnectionState
    from .types import DataSendMessage


@runtime_checkable
class Identifier(Protocol):
    """An ABC that details the common operations on a Lightspeed model.

    Almost all :ref:`Lightspeed models <lightspeed_api_models>` meet this
    abstract base class.

    If you want to create a snowflake on your own, consider using
    :class:`.Object`.

    Attributes
    -----------
    id: :class:`str`
        The model's unique ID.
    """

    id: str


class Messageable(ABC):
    __slots__ = ('_state',)

    _state: ConnectionState

    @abstractmethod
    async def _get_chat(self) -> MessageableChat: ...

    async def history(self) -> AsyncIterator[Message]:
        """|coro|

        Retrieves the chat history.

        Yields
        ------
        :class:`Message`
            The message.
        """

        chat = await self._get_chat()

        data = await self._state.http.get_chat_messages(chat.id)
        for d in data:
            yield Message(data=d, chat=chat)

    async def send(self, content: Any) -> Message:
        """|coro|

        Sends a message in chat.

        Parameters
        ----------
        content: :class:`str`
            The message content.

        Returns
        -------
        :class:`Message`
            The message that was sent.
        """
        payload: DataSendMessage = {'content': str(content)}

        chat = await self._get_chat()
        data = await self._state.http.create_chat_message(chat.id, payload)
        return Message(data=data, chat=chat)


if TYPE_CHECKING:
    from .stream import PartialStream, Stream, LargeStream
    from typing import TypeAlias, Union

    MessageableChat: TypeAlias = 'Union[PartialStream, Stream, LargeStream]'

__all__ = ('Identifier', 'Messageable', 'MessageableChat')
