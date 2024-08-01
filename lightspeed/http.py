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
import asyncio
import logging
import sys
from typing import Any, ClassVar, Coroutine, Dict, List, Optional, TYPE_CHECKING, TypeVar, Union
from urllib.parse import quote as _uriquote

from . import __version__, types, utils
from .errors import HTTPException, RateLimited, Forbidden, NotFound, LightspeedServerError, LoginFailure
from .utils import MISSING

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['content-type'] == 'application/json':
            return utils._from_json(text)
    except KeyError:
        # Thanks Cloudflare
        pass

    return text


class Route:
    DEFAULT_BASE: ClassVar[str] = 'https://api.lightspeed.tv'

    __slots__ = (
        'path',
        'method',
        'parameters',
    )

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.method: str = method
        self.path: str = path
        self.parameters: Dict[str, Any] = parameters

    def url(self, base: str) -> str:
        url = base + self.path
        if self.parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in self.parameters.items()})
        return url


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Lightspeed API."""

    __slots__ = (
        'connector',
        '__session',
        'base',
        'token',
        'proxy',
        'proxy_auth',
        'http_trace',
        'user_agent',
        'max_ratelimit_timeout',
    )

    def __init__(
        self,
        connector: Optional[aiohttp.BaseConnector] = None,
        *,
        base: str = MISSING,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        http_trace: Optional[aiohttp.TraceConfig] = None,
        max_ratelimit_timeout: Optional[float] = None,
    ) -> None:
        self.connector: Optional[aiohttp.BaseConnector] = connector
        self.__session: aiohttp.ClientSession = MISSING  # filled in static_login

        self.base: str = Route.DEFAULT_BASE if base is MISSING else base.rstrip('/')
        self.token: Optional[str] = None
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth
        self.http_trace: Optional[aiohttp.TraceConfig] = http_trace
        self.max_ratelimit_timeout: Optional[float] = (
            max(30.0, max_ratelimit_timeout) if max_ratelimit_timeout else None
        )

        user_agent = 'Lightspeed.py (https://github.com/MCausc78/lightspeed.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(
        self,
        route: Route,
        **kwargs: Any,
    ) -> Any:
        method = route.method
        url = route.url(self.base)

        headers: Dict[str, str] = {
            'User-Agent': self.user_agent,
        }

        try:
            new_headers = kwargs.pop('headers')
        except KeyError:
            pass
        else:
            headers.update(new_headers)

        if self.token is not None:
            headers['X-Session-Token'] = self.token

        # some checking if it's a JSON request
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils._to_json(kwargs.pop('json'))

        # Proxy support
        if self.proxy is not None:
            kwargs['proxy'] = self.proxy
        if self.proxy_auth is not None:
            kwargs['proxy_auth'] = self.proxy_auth

        kwargs['headers'] = headers
        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        for tries in range(5):
            async with self.__session.request(method, url, **kwargs) as response:
                _log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), response.status)

                data = await json_or_text(response)

                if 300 > response.status >= 200:
                    _log.debug('%s %s has received %s', method, url, data)
                    return data

                # we are being rate limited
                if response.status == 429:
                    if isinstance(data, str):
                        # Banned by Cloudflare more than likely.
                        raise HTTPException(response, data)

                    retry_after: float = data['retry_after'] / 1000
                    if self.max_ratelimit_timeout and retry_after > self.max_ratelimit_timeout:
                        _log.warning(
                            'We are being rate limited. %s %s responded with 429. Timeout of %.2f was too long, erroring instead.',
                            method,
                            url,
                            retry_after,
                        )
                        raise RateLimited(retry_after)

                    fmt = 'We are being rate limited. %s %s responded with 429. Retrying in %.2f seconds.'
                    _log.warning(fmt, method, url, retry_after)

                    await asyncio.sleep(retry_after)
                    _log.debug('Done sleeping for the rate limit. Retrying...')

                    continue

                if response.status in (502, 504, 524):
                    await asyncio.sleep(1 + tries * 2)
                    continue

                # the usual error cases
                if response.status == 403:
                    raise Forbidden(response, data)
                elif response.status == 404:
                    raise NotFound(response, data)
                elif response.status >= 500:
                    raise LightspeedServerError(response, data)
                else:
                    raise HTTPException(response, data)

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise LightspeedServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    # state management

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    # login management

    async def startup(self) -> None:
        self.__session = aiohttp.ClientSession(
            connector=self.connector,
            trace_configs=None if self.http_trace is None else [self.http_trace],
        )

    async def static_login(self, token: str) -> types.User:
        await self.startup()

        old_token = self.token
        self.token = token

        try:
            data = await self.get_me()
        except HTTPException as exc:
            self.token = old_token
            if exc.status == 401:
                raise LoginFailure('Improper token has been passed.') from exc
            raise

        return data

    # Regions
    def get_regions(self) -> Response[List[types.Region]]:
        """Fetch all streaming regions."""
        return self.request(Route('GET', '/regions'))

    # Streams
    def get_streams(self) -> Response[List[types.AggregateStream]]:
        """Find global streams"""
        return self.request(Route('GET', '/streams/'))

    def create_stream(self, payload: types.DataCreateStream, /) -> Response[types.Stream]:
        """Enable streaming on a user account.

        Requires creating a user first."""
        return self.request(Route('PUT', '/streams/'), json=payload)

    def my_stream(self) -> Response[types.Stream]:
        """Fetch own stream information"""
        return self.request(Route('GET', '/streams/@me'))

    def edit_my_stream(self, payload: types.DataEditStream, /) -> Response[types.Stream]:
        """Edit stream information."""
        return self.request(Route('PATCH', '/streams/@me'), json=payload)

    def get_stream(self, user_path: str, /) -> Response[types.AggregateStream]:
        """Fetch a stream by stream path"""
        return self.request(Route('GET', '/streams/{user_path}', user_path=user_path))

    def get_stream_bans(self, stream_id: str, /) -> Response[types.ResponseBanList]:
        """Fetch all banned users in a stream"""
        return self.request(Route('GET', '/streams/{stream_id}/bans', stream_id=stream_id))

    def get_stream_moderators(self, stream_id: str, /) -> Response[List[types.User]]:
        """Fetch all moderator information for stream"""
        return self.request(Route('GET', '/streams/{stream_id}/moderators', stream_id=stream_id))

    def reset_stream_token(self) -> Response[types.Stream]:
        """Reset the token used for this account's stream."""
        return self.request(Route('POST', '/streams/reset_token'))

    # Moderation
    def ban(self, stream_id: str, user_id: str, payload: types.DataBanUser, /) -> Response[types.Ban]:
        """Permamently ban a user from talking."""
        return self.request(
            Route('PUT', '/streams/{stream_id}/bans/{user_id}', stream_id=stream_id, user_id=user_id), json=payload
        )

    def unban(self, stream_id: str, user_id: str, /) -> Response[None]:
        """Unban a user."""
        return self.request(
            Route('DELETE', '/streams/{stream_id}/bans/{user_id}', stream_id=stream_id, user_id=user_id)
        )

    def promote(self, stream_id: str, user_id: str, /) -> Response[None]:
        """Give a target user moderation powers on a stream."""
        return self.request(Route('PUT', '/streams/{stream_id}/mods/{user_id}', stream_id=stream_id, user_id=user_id))

    def demote(self, stream_id: str, user_id: str, /) -> Response[None]:
        """Take away a target user's moderation powers on a stream."""
        return self.request(
            Route('DELETE', '/streams/{stream_id}/mods/{user_id}', stream_id=stream_id, user_id=user_id)
        )

    # Followers
    def follow_stream(self, stream_id: str, /) -> Response[None]:
        return self.request(Route('PUT', '/streams/{stream_id}/follow', stream_id=stream_id))

    def unfollow_stream(self, stream_id: str, /) -> Response[None]:
        return self.request(Route('DELETE', '/streams/{stream_id}/follow', stream_id=stream_id))

    # Users
    def get_me(self) -> Response[types.User]:
        """Fetch own user."""
        return self.request(Route('GET', '/users/@me'))

    def create_user(self, payload: types.DataCreateUser, /) -> Response[types.User]:
        """Create a new user profile."""
        return self.request(Route('PUT', '/users/@me'), json=payload)

    def edit_my_user(self, payload: types.DataEditUser, /) -> Response[types.User]:
        """Edit user information."""
        return self.request(Route('PATCH', '/users/@me'), json=payload)

    def get_user(self, user_path: str, /) -> Response[types.User]:
        """Fetch user using path"""
        return self.request(Route('GET', '/users/{user_path}', user_path=user_path))

    def my_bans(self) -> Response[List[types.BanInformation]]:
        """Fetch all of your bans"""
        return self.request(Route('GET', '/users/bans'))

    # Categories
    def create_category(self, payload: types.DataCreateCategory, /) -> Response[types.Category]:
        """Create a new category of streams."""
        return self.request(Route('POST', '/categories/create'), json=payload)

    def delete_category(self, category_id: str, /) -> Response[None]:
        """Delete a streaming category."""
        return self.request(Route('DELETE', '/categories/{category_id}', category_id=category_id))

    def edit_category(self, category_id: str, payload: types.DataEditCategory, /) -> Response[types.Category]:
        """Change information for an existing category."""
        return self.request(Route('PATCH', '/categories/{category_id}', category_id=category_id), json=payload)

    def list_categories(self) -> Response[List[types.Category]]:
        """List streaming categories available."""
        return self.request(Route('GET', '/categories/'))

    # Chat
    def get_chat_messages(self, chat_id: str, /) -> Response[List[types.Message]]:
        """Fetch chat message history for a stream."""
        return self.request(Route('GET', '/chat/{chat_id}/messages', chat_id=chat_id))

    def create_chat_message(self, chat_id: str, payload: types.DataSendMessage, /) -> Response[types.Message]:
        """Send a message to a stream chat."""
        return self.request(Route('POST', '/chat/{chat_id}/messages', chat_id=chat_id), json=payload)

    def delete_chat_message(self, chat_id: str, message_id: str, /) -> Response[None]:
        """Delete a message from chat by its id."""
        return self.request(
            Route('DELETE', '/chat/{chat_id}/messages/{message_id}', chat_id=chat_id, message_id=message_id)
        )

    # Admin
    def list_stream_invites(self) -> Response[List[types.InviteInformation]]:
        """List all pending and used stream invites."""
        return self.request(Route('GET', '/admin/invites'))

    def create_stream_invite(self, payload: types.DataCreateInvite, /) -> Response[None]:
        """Create a new invite for streaming."""
        return self.request(Route('POST', '/admin/invites'), json=payload)

    def delete_stream_invite(self, invite_code: str, /) -> Response[None]:
        """Delete an existing unclaimed stream invite."""
        return self.request(Route('DELETE', '/admin/invites/{invite_code}', invite_code=invite_code))

    def edit_stream_as_admin(self, stream_id: str, payload: types.DataEditStream, /) -> Response[types.Stream]:
        """Edit stream information."""
        return self.request(Route('PATCH', '/admin/streams/{stream_id}', stream_id=stream_id), json=payload)

    def edit_user_as_admin(self, user_id: str, payload: types.DataEditUser, /) -> Response[types.User]:
        """Edit user information."""
        return self.request(Route('PATCH', '/admin/users/{user_id}', user_id=user_id), json=payload)

    def get_streams_as_admin(self) -> Response[List[types.AggregateStream]]:
        """Find all live streams regardless of if they're hidden"""
        return self.request(Route('GET', '/admin/livestreams'))

    def stop_stream_as_admin(self, stream_id: str, /) -> Response[types.Stream]:
        """Disconnect all users from a stream and stop it."""
        return self.request(Route('POST', '/admin/streams/{stream_id}/stop', stream_id=stream_id))

    def report(self, payload: types.DataReportContent, /) -> Response[None]:
        """Report something to Lightspeed."""
        return self.request(Route('POST', '/reports/send'), json=payload)


__all__ = ('HTTPClient',)
