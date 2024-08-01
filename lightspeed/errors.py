"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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
from typing import Dict, Optional, TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse


class LightspeedException(Exception):
    """Base exception class for lightspeed.py

    Ideally speaking, this could be caught to handle any exceptions raised from this library.
    """

    pass


class ClientException(LightspeedException):
    """Exception that's raised when an operation in the :class:`Client` fails.

    These are usually for exceptions that happened due to user input.
    """

    pass


class HTTPException(LightspeedException):
    """Exception that's raised when an HTTP request operation fails.

    Attributes
    ------------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`.

    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    """

    def __init__(self, response: ClientResponse, message: Optional[Union[str, Dict[str, Any]]]) -> None:
        self.response: ClientResponse = response
        self.status: int = response.status
        self.text: str = f'{message!r}'

        fmt = '{0.status} {0.reason}'
        if len(self.text):
            fmt += ': {1}'

        super().__init__(fmt.format(self.response, self.text))


class RateLimited(LightspeedException):
    """Exception that's raised for when status code 429 occurs
    and the timeout is greater than the configured maximum using
    the ``max_ratelimit_timeout`` parameter in :class:`Client`.

    This is not raised during global ratelimits.

    Since sometimes requests are halted pre-emptively before they're
    even made, this **does not** subclass :exc:`HTTPException`.

    Attributes
    ------------
    retry_after: :class:`float`
        The amount of seconds that the client should wait before retrying
        the request.
    """

    def __init__(self, retry_after: float):
        self.retry_after = retry_after
        super().__init__(f'Too many requests. Retry in {retry_after:.2f} seconds.')


class Forbidden(HTTPException):
    """Exception that's raised for when status code 403 occurs.

    Subclass of :exc:`HTTPException`
    """

    pass


class NotFound(HTTPException):
    """Exception that's raised for when status code 404 occurs.

    Subclass of :exc:`HTTPException`
    """

    pass


class LightspeedServerError(HTTPException):
    """Exception that's raised for when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.
    """

    pass


class LoginFailure(ClientException):
    """Exception that's raised when the :meth:`Client.login` function
    fails to log you in from improper credentials or some other misc.
    failure.
    """

    pass


__all__ = (
    'ClientException',
    'HTTPException',
    'RateLimited',
    'Forbidden',
    'NotFound',
    'LightspeedServerError',
    'LoginFailure',
)
