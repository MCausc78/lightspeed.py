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

from typing import List, Literal, NotRequired, Optional, TypedDict, Union


class Region(TypedDict):
    # [optional+nullable] Internal ID
    _id: str
    # [optional+nullable] Publicly accessible server hostname
    hostname: str
    # [optional+nullable] URL to connect to this server's signaling service
    signaling: str
    # [optional+nullable] URL to connect to this server's ingest service
    ingest: str
    # [optional+nullable] The location of this server
    location: str
    # [optional+nullable] Last ping from this server
    # If a server has not sent a ping within the past 30 seconds, assume it to be offline.
    last_ping: NotRequired[Optional[str]]


# Any user live stream
class Stream(TypedDict):
    # [optional+nullable] Internal ID
    _id: NotRequired[str]
    # [optional+nullable] ID used for FTL protocol
    ftl_id: NotRequired[Optional[int]]
    # [optional+nullable] Stream Title
    title: str
    # [optional+nullable] Stream Description
    description: NotRequired[str]
    # [optional+nullable] ID of thumbnail file
    thumbnail: NotRequired[str]
    # [optional] Stream Tags
    tags: NotRequired[List[str]]
    # [optional+nullable] Stream Token for FTL
    token: NotRequired[Optional[str]]
    # [optional+nullable] Object providing additional information while live
    live: NotRequired[Optional[Live]]
    # [optional+default='default']
    category: NotRequired[str]
    # [optional] IDs of moderators
    moderators: NotRequired[List[str]]
    # [optional+default=true] Whether to record VODs for this stream
    record: NotRequired[bool]
    # [optional] Whether this stream is currently prohibited from going live
    suspended: NotRequired[bool]
    # [optional+nullable] RTMP URL to relay the stream to
    rtmp_relay: NotRequired[Optional[str]]
    # [optional+nullable] Time at which the last stream ended
    last_streamed: NotRequired[Optional[str]]


# Active live stream
class Live(TypedDict):
    # [] When this stream started
    started_at: str
    # [] Region clients should connect to in order to watch
    region: str
    # [optional] Enum determining how clients should connect to this live stream
    controller: NotRequired[Controller]


Controller = Literal['Inhouse', 'Mist']


# Stream Data
class DataCreateStream(TypedDict):
    # Invite code provided by Lightspeed team
    invite: str


# Stream Data
class DataEditStream(TypedDict):
    # [optional] Stream title
    title: NotRequired[str]
    # [optional] Stream description
    description: NotRequired[str]
    # [optional] Attachment Id used for thumbnail
    thumbnail: NotRequired[Optional[str]]
    # [optional] Stream tags
    tags: NotRequired[List[str]]
    # [optional] Stream category id
    category: NotRequired[str]
    # [optional] RTMP Relay
    rtmp_relay: NotRequired[str]
    # [optional] Whether this stream is prohibited from going live
    suspended: NotRequired[bool]


# Combined stream information
class AggregateStream(TypedDict):
    # [optional+nullable] Internal ID
    _id: str
    # [] User information
    user: User
    # [] Stream information
    stream: Stream
    # [] Category information
    category: Category
    # [optional+nullable]
    region: NotRequired[Optional[Region]]
    # [optional+nullable] Number of followers this stream has
    follower_count: NotRequired[Optional[int]]


class User(TypedDict):
    # [optional+nullable] Internal ID
    _id: str
    # [] Path at which this user is accessible
    path: str
    # [] Case-sensitive username
    username: str
    # [optional+nullable] ID of avatar file
    avatar: NotRequired[Optional[str]]
    # [optional+nullable] ID of banner file
    banner: NotRequired[Optional[str]]
    # [optional] User profile bio
    bio: NotRequired[str]
    # [optional] Social links
    social_links: NotRequired[List[SocialLink]]
    # [optional] Accent Colour
    accent_colour: NotRequired[str]
    # [optional] Whether this user is privileged
    privileged: NotRequired[bool]
    # [optional] Hide user and their stream from public discovery
    hidden: NotRequired[bool]
    # [optional] Whether this user is globally chat muted
    chat_restricted: NotRequired[bool]
    # [optional] Request only: Other users this user is following
    following: NotRequired[List[User]]
    # [optional] Request only: IDs of other users this user is following
    following_ids: NotRequired[List[str]]


class SocialLink(TypedDict):
    title: str
    link: str


class Category(TypedDict):
    # [optional+nullable] Internal ID
    _id: NotRequired[str]
    # [] Title for this category
    title: str
    # [optional+nullable] ID of cover picture
    cover: NotRequired[Optional[str]]
    # [optional] Category description
    description: NotRequired[str]


# Ban List
class ResponseBanList(TypedDict):
    bans: List[Ban]
    users: List[User]


# Representation of a chat ban on Lightspeed
class Ban(TypedDict):
    # [optional+nullable] Internal ID
    _id: str
    # [] Stream ID
    stream_id: str
    # [] User ID
    user_id: str
    # [] Mod ID
    mod_id: str
    # [optional] Ban Reason
    reason: NotRequired[str]
    # [optional+nullable] Time to expire
    expires: NotRequired[Optional[str]]


# Ban Data
class DataBanUser(TypedDict):
    # [optional+nullable] Time at which this ban expires
    expires: NotRequired[Optional[str]]


# User Data
class DataCreateUser(TypedDict):
    # [] Username
    username: str


# User Data
class DataEditUser(TypedDict):
    # [optional+nullable] New username
    username: NotRequired[str]
    # [optional+nullable] Attachment Id used for avatar
    avatar: NotRequired[Optional[str]]
    # [optional+nullable] Attachment Id used for banner
    banner: NotRequired[Optional[str]]
    # [optional+nullable] Profile bio
    bio: NotRequired[Optional[str]]
    # [optional+nullable] List of social links
    social_links: NotRequired[Optional[List[SocialLink]]]
    # [optional+nullable] Whether to hide the user and stream from public discovery
    hidden: NotRequired[Optional[bool]]
    # [optional+nullable] Whether to restrict the user from chatting globally
    chat_restricted: NotRequired[Optional[bool]]


# Information about a user's ban on Lightspeed
class BanInformation(TypedDict):
    # [] Stream ID
    stream_id: str
    # [optional+nullable] Time to expire
    expires: NotRequired[Optional[str]]


# Category Data
class DataCreateCategory(TypedDict):
    # [] Category title
    title: str
    # [optional+nullable] Attachment Id for cover photo
    cover: NotRequired[Optional[str]]
    # [] Category description
    description: str


# Category Data
class DataEditCategory(TypedDict):
    # [optional+nullable] Category title
    title: NotRequired[str]
    # [optional+nullable] Attachment Id for category photo
    cover: NotRequired[Optional[str]]
    # [optional+nullable] Category description
    description: NotRequired[Optional[str]]


class Message(TypedDict):
    # [optional+nullable] Internal ID
    _id: str
    # [] Stream ID
    stream_id: str
    # [optional+nullable] User
    author: UserInformation
    # [] User ID
    author_id: str
    # [] Message content
    content: str


# Minimal information to display user in chat or similar location
class UserInformation(TypedDict):
    # [] User ID
    id: str
    # [] Path at which this user is accessible
    path: str
    # [] Case-sensitive username
    username: str
    # [optional+nullable] ID of avatar file
    avatar: NotRequired[Optional[str]]
    # [optional] Accent Colour
    accent_colour: NotRequired[str]


# Message Data
class DataSendMessage(TypedDict):
    # [] Message content
    content: str


# Invite Data
class DataCreateInvite(TypedDict):
    # [] Invite code
    code: str


# Invite Information
# Newtype to avoid errors with schemas
class InviteInformation(TypedDict):
    id: str
    used: bool
    claimed_by: NotRequired[Optional[str]]


# Report Data
class DataReportContent(TypedDict):
    # [] Content to report
    content: ReportedContent
    # [] Report description
    reason: str


class StreamReportedContent(TypedDict):
    type: Literal['Stream']
    # [] Path to stream
    path: str


class UserReportedContent(TypedDict):
    type: Literal['User']
    # [] ID of the user
    id: str


ReportedContent = Union[StreamReportedContent, UserReportedContent]

__all__ = (
    'Region',
    'Stream',
    'Live',
    'Controller',
    'DataCreateStream',
    'DataEditStream',
    'AggregateStream',
    'User',
    'SocialLink',
    'Category',
    'ResponseBanList',
    'Ban',
    'DataBanUser',
    'DataCreateUser',
    'DataEditUser',
    'BanInformation',
    'DataCreateCategory',
    'DataEditCategory',
    'Message',
    'UserInformation',
    'DataSendMessage',
    'DataCreateInvite',
    'InviteInformation',
    'DataReportContent',
    'StreamReportedContent',
    'UserReportedContent',
    'ReportedContent',
)
