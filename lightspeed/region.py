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

from typing import Optional, TYPE_CHECKING

from .utils import parse_time

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types import Region as RegionPayload


class Region:
    """Represents a streaming region.

    Attributes
    ----------
    id: :class:`str`
        The region's ID.
    hostname: :class:`str`
        The public server hostname.
    signaling_url: :class:`str`
        The WS URL to use when connecting to this server's signaling service.
    ingest_url: :class:`str`
        The FTL URL to use when connecting to this server's ingest service.
    location: :class:`str`
        The server's location.
    last_pinged_at: Optional[:class:`datetime.datetime`]
        The datetime when server was lastly pinged at.
        If a server has not sent a ping within the past 30 seconds, assume it to be offline.
    """

    __slots__ = ('_state', 'id', 'hostname', 'signaling_url', 'ingest_url', 'location', 'last_pinged_at')

    def __init__(self, *, data: RegionPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id: str = data['_id']
        self.hostname: str = data['hostname']
        self.signaling_url: str = data['signaling']
        self.ingest_url: str = data['ingest']
        self.location: str = data['location']
        self.last_pinged_at: Optional[datetime.datetime] = parse_time(data.get('last_ping'))

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id} hostname={self.hostname!r} signaling_url={self.signaling_url!r} ingest_url={self.ingest_url!r} location={self.location!r} last_pinged_at={self.last_pinged_at!r}>'


__all__ = ('Region',)
