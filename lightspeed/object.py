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

from .mixins import Hashable
from .utils import MISSING

from typing import (
    TYPE_CHECKING,
    Type,
)

if TYPE_CHECKING:
    from . import abc


class Object(Hashable):
    """Represents a generic Lightspeed object.

    The purpose of this class is to allow you to create 'miniature'
    versions of data classes if you want to pass in just an ID. Most functions
    that take in a specific data class with an ID can also take in this class
    as a substitute instead. Note that even though this is the case, not all
    objects (if any) actually inherit from this class.

    .. container:: operations

        .. describe:: x == y

            Checks if two objects are equal.

        .. describe:: x != y

            Checks if two objects are not equal.

        .. describe:: hash(x)

            Returns the object's hash.

    Attributes
    -----------
    id: :class:`int`
        The ID of the object.
    type: Type[:class:`abc.Identifier`]
        The lightspeed.py model type of the object, if not specified, defaults to this class.
    """

    def __init__(self, id: str, *, type: Type[abc.Identifier] = MISSING):
        self.id: str = id
        self.type: Type[abc.Identifier] = type or self.__class__

    def __repr__(self) -> str:
        return f'<Object id={self.id!r} type={self.type!r}>'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (self.type, self.__class__)):
            return self.id == other.id
        return NotImplemented

    __hash__ = Hashable.__hash__


OLDEST_OBJECT = Object(id='00000000000000000000000000')

__all__ = (
    'Object',
    'OLDEST_OBJECT',
)
