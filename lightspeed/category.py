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

from .utils import MISSING

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types import Category as CategoryPayload, DataEditCategory


class PartialCategory:
    """Represents a partial streaming category.

    Attributes
    ----------
    id: :class:`str`
        The category's ID.
    """

    __slots__ = (
        '_state',
        'id',
    )

    def __init__(self, *, id: str, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id: str = id

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r}>'

    async def delete(self) -> None:
        """|coro|

        Deletes the category.
        """
        await self._state.http.delete_category(self.id)

    async def edit(
        self,
        *,
        title: str = MISSING,
        cover_image: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
    ) -> None:
        """|coro|

        Edits the category.

        Parameters
        ----------
        title: :class:`str`
            The new category title.
        cover_image: Optional[:class:`str`]
            The new category's cover image ID.
        description: Optional[:class:`str`]
            The new category's description.

        Returns
        -------
        :class:`Category`
            The newly updated category.
        """
        payload: DataEditCategory = {}

        if title is not MISSING:
            payload['title'] = title

        if cover_image is not MISSING:
            payload['cover'] = cover_image

        if description is not MISSING:
            payload['description'] = description

        await self._state.http.edit_category(self.id, payload)


class Category(PartialCategory):
    """Represents a streaming category.

    Attributes
    ----------
    id: :class:`str`
        The category's ID.
    title: :class:`str`
        The category title.
    cover_image_id: Optional[:class:`str`]
        The category cover image ID.
    description: Optional[:class:`str`]
        The category description.
    """

    __slots__ = (
        '_state',
        'id',
        'title',
        'cover_image_id',
        'description',
    )

    def __init__(self, *, data: CategoryPayload, state: ConnectionState) -> None:
        super().__init__(id=data.get('_id', 'default'), state=state)
        self.title: str = data['title']
        self.cover_image_id: Optional[str] = data.get('cover')
        self.description: Optional[str] = data.get('description')

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} title={self.title!r} cover_image_id={self.cover_image_id!r} description={self.description!r}>'


__all__ = ('PartialCategory', 'Category')
