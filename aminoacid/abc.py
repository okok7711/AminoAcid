from __future__ import annotations

from abc import ABC
from base64 import b64encode, urlsafe_b64decode
from importlib.util import find_spec
from os import PathLike, path
from typing import TYPE_CHECKING, BinaryIO, Callable, Dict, List, Optional, Union

from .util import str_to_ts

_ORJSON = find_spec("orjson")
if _ORJSON:
    import orjson as json
else:
    import json


if TYPE_CHECKING:
    from . import Bot


class AminoBaseClass(ABC):
    """This is the base class for all other classes defined by this library, except for clients and exceptions."""

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        try:  #! pdoc complained that vars(self) is a function (which it is NOT) so there's this try/except here to catch that
            _temp = [
                f"{attr}={value!r}, "
                for attr, value in vars(self).items()
                if value
                and not isinstance(
                    value,
                    (Callable, type(self.client))
                    if "client" in dir(self)
                    else Callable,
                )
            ]
            return f"{type(self).__name__}({''.join(_temp).rstrip(', ')})"
        except AttributeError:
            return f"{type(self).__name__}()"


class MessageAble(AminoBaseClass):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__()

    async def send(self, content: str, **kwargs) -> Message:
        """Send a Message to the messageable object

        Parameters
        ----------
        content : str
            Content of the message, cannot be empty, must be within 2000 characters
        embed : Embed, optional
            The embed to send alongside the message, by default ...

        Returns
        -------
        Message
            Message object of the sent message
        """
        if isinstance(self, Message):
            return await self.client.send_message(
                content=content, threadId=self.threadId, ndcId=self.ndcId, **kwargs
            )
        if isinstance(self, Context):
            return await self.client.send_message(
                content=content,
                threadId=self.message.threadId,
                ndcId=self.message.ndcId,
                **kwargs,
            )
        if isinstance(self, Thread):
            return await self.client.send_message(
                content=content, threadId=self.id, ndcId=self.ndcId, **kwargs
            )
        if isinstance(self, User):
            return await self.client.message_user(
                content=content,
                userId=self.id,
                ndcId=self.ndcId if "ndcId" in dir(self) else 0,
                **kwargs,
            )


class Context(MessageAble):
    """Context of a message, this is passed into `aminoacid.util.UserCommand`s as the first positional argument"""

    def __init__(
        self,
        client: Bot,
        message: Message,
    ) -> None:
        """Initialises the Context

        Parameters
        ----------
        client : Bot
            The currently running client, used for replying, deleting, etc.
        message : Message
            The message the context describes
        """
        self.client = client
        self.message = message
        self.thread = message.thread
        self.author = message.author

        super().__init__(bot=client)

    async def reply(self, content: str, **kwargs):
        """Replies to the message described by the context (`self.message`)

        Parameters
        ----------
        content : str
            Content of the message to reply with
        """
        await super().send(content, replyMessageId=self.message.id, **kwargs)


class User(MessageAble):
    nickname: str
    icon: str
    content: str
    id: str
    status: int
    moodSticker: dict
    itemsCount: int
    consecutiveCheckInDays: int
    modifiedTime: str
    followingStatus: int
    onlineStatus: int
    accountMembershipStatus: int
    isGlobal: bool = True
    avatarFrameId: str
    fanClubList: list = []
    reputation: int = 0
    postsCount: int = 0
    avatarFrame: Frame
    membersCount: int
    mediaList: list
    isNicknameVerified: bool = False
    visitorsCount: int = 0
    mood: None
    level: int = 0
    notificationSubscriptionStatus: int = 0
    settings: dict
    pushEnabled: bool
    membershipStatus: int
    joinedCount: int
    role: int = 0
    commentsCount: int = 0
    aminoId: str
    createdTime: str
    extensions: dict
    visitPrivacy: int = 1
    storiesCount: int = 0

    client: Bot

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `User` object, calls `from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `User` with, by default {}
        """
        self.from_dict({**data, **kwargs})
        super().__init__(bot=self.client)

    def from_dict(self, data: dict):
        """Create a new `User` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `User` object from
        """
        self.nickname = data.pop("nickname", "")
        self.content = data.pop("content", "")
        self.icon = data.pop("icon", "")
        self.id = data.pop("uid", "")
        self.client = data.pop("client")

    async def send(self, content: str, **kwargs) -> Message:
        return await super().send(content, **kwargs)

    async def get(self) -> User:
        """Get the complete `User` object, used when a `User` is received partially by the socket to get the missing information."""
        return await self.client.fetch_user(self.id)


class Member(User):
    ndcId: int

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Member` object, calls `from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Member` with, by default {}
        """
        self.from_dict({**data, **kwargs})
        super().__init__(data, **kwargs)

    def from_dict(self, data: dict):
        """Create a new `Member` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Member` object from
        """
        self.ndcId = data.pop("ndcId")
        return super().from_dict(data)


class Message(AminoBaseClass):
    id: str
    type: int
    content: str
    author: User
    threadId: str
    ndcId: Optional[int] = None
    isHidden: bool
    includedInSummary: bool
    createdTime: int
    extensions: dict
    alertOption: int
    membershipStatus: int
    chatBubbleId: str
    chatBubbleVersion: int
    clientRefId: int
    mediaType: int

    client: Bot

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Message` object, calls `from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Message` with, by default {}
        """
        self.from_dict({**data, **kwargs})
        super().__init__()
        self.startswith = self.content.startswith

    def from_dict(self, data: dict):
        """Create a new `Message` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Message` object from
        """
        self.client = data.pop("client")

        self.nickname = data.pop("nickname", "")
        self.content = data.pop("content", "")
        self.id = data.pop("messageId", "")
        self.threadId = data.pop("threadId", "")
        self.ndcId = data.pop("ndcId", 0)
        self.thread = Thread(id=self.threadId, ndcId=self.ndcId, client=self.client)
        if self.ndcId:
            self.author = Member(
                data.pop("author", {}), client=self.client, ndcId=self.ndcId
            )
        else:
            self.author = User(data.pop("author", {}), client=self.client)
        self.type = data.pop("type", None)

        self.createdTime = str_to_ts(data.pop("createdTime", ""))
        self.alertOption = data.pop("alertOption", None)
        self.chatBubbleId = data.pop("chatBubbleId", "")
        self.clientRefId = data.pop("clientRefId", 0)
        self.extensions = data.pop("extensions", {})
        self.isHidden = data.pop("isHidden", False)
        self.membershipStatus = data.pop("membershipStatus", 0)
        self.includedInSummary = data.pop("includedInSummary", True)
        self.mediaType = data.pop("mediaType", 0)

    async def get(self):
        """Get the complete `Message` object, used when a `Message` is received partially by the socket to get the missing information."""
        await self.client.fetch_message(
            messageId=self.id, threadId=self.thread.id, ndcId=self.ndcId
        )


class Thread(MessageAble):
    id: str
    content: str
    author: User
    ndcId: Optional[int] = None
    title: str

    # TODO: FINISH THIS

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Thread` object, calls `from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Thread` with, by default {}
        """
        self.from_dict({**data, **kwargs})
        super().__init__(bot=self.client)

    def from_dict(self, data: dict):
        """Create a new `Thread` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Thread` object from
        """
        self.client = data.pop("client")

        self.title = data.pop("title", "")
        self.content = data.pop("content", "")
        self.author = data.pop("author", "")
        self.id = data.pop("threadId", "")
        self.ndcId = data.pop("ndcId", "")

    async def send(self, content: str, **kwargs) -> Message:
        return await super().send(content, **kwargs)

    async def get(self):
        """Get the complete `Thread` object, used when a `Thread` is received partially by the socket to get the missing information."""
        self.from_dict(
            (await self._bot.get_thread(ndcId=self.ndcId, threadId=self.id)).__dict__
        )


class Community(AminoBaseClass):
    userAddedTopicList: Optional[List]
    agent: Member
    listedStatus: int
    probationStatus: int
    themePack: dict
    membersCount: int
    primaryLanguage: str
    communityHeat: int
    strategyIngo: str
    tagline: str
    joinType: int
    status: int
    launchPage: dict
    modifiedTime: int
    ndcId: str
    activeInfo: Optional[Dict]
    link: str
    icon: str
    endpoint: str
    name: str
    templateId: int
    createdTime: int
    promotionalMediaList: Optional[List]

    # TODO: Implement this!!

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Community` object, calls `from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Community` with, by default {}
        """
        self.from_dict({**data, **kwargs})
        super().__init__()

    def from_dict(self, data: dict):
        """Create a new `Community` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Community` object from
        """
        self.client = data.pop("client")

        self.name = data.pop("name", "")
        self.id = data.pop("ndcId", "")


class Embed(AminoBaseClass):
    def __init__(
        self,
        objectId: str,
        objectType: int,
        link: str,
        title: str,
        content: str,
        mediaList: list,
    ) -> None:

        self.id = objectId
        self.type = objectType
        self.link = link
        self.title = title
        self.content = content
        self.mediaList = mediaList

        super().__init__()

    def __dict__(self):
        return {
            "objectId": self.id,
            "objectType": self.type,
            "link": self.link,
            "title": self.title,
            "content": self.content,
            "mediaList": self.mediaList,
        }


class linkSnippet(AminoBaseClass):
    def __init__(self, link: str, image: Union[BinaryIO, PathLike]) -> None:
        """Initialises a new Link Snippet object to use for sending them in chat

        Parameters
        ----------
        link : str
            link of the snipped
        image : Union[BinaryIO, PathLike]
            Either a Path of the image or an IO representation of the image
        """
        if isinstance(image, PathLike):
            if path.exists(image):
                with open(image, "rb") as f:
                    self.image = b64encode(f.read())
        else:
            self.image = b64encode(image.read())
        self.link = link
        super().__init__()

    async def prepare(self, client: Bot) -> dict:
        """Prepare the link snippet by uploading `self.image` to amino servers via `aminoacid.Bot.upload_image()`

        Parameters
        ----------
        client : Bot
            Bot object to upload the image

        Returns
        -------
        dict
            Dict containing all the information of the linkSnippet object
        """
        return {
            "link": self.link,
            "mediaType": 100,
            "mediaUploadValue": client.upload_image(self.image),
            "mediaUploadValueContentType": "image/png",
        }


class Frame(AminoBaseClass):
    # TODO: Add Frame class for OOP
    ...


class Bubble(AminoBaseClass):
    # TODO: Same as Frame
    ...


class Notification(AminoBaseClass):
    payload: dict
    timestamp: int
    messageType: int
    ndcId: str
    threadId: str
    isHidden: bool
    id: str
    type: int

    def __init__(self, data: dict) -> None:
        self.from_dict(data)
        super().__init__()

    def from_dict(self, data: dict):
        """Create a new `Notification` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Notification` object from
        """

        self.payload = data.pop("payload", {})

        self.timestamp = self.payload.get("ts", "")
        self.threadId = self.payload.get("tid", "")
        self.isHiddem = self.payload.get("isHidden", "")
        self.id = self.payload.get("id", "")
        self.ndcId = self.payload.get("ndcId", "")
        self.messageType = self.payload.get("msgType", 0)
        self.type = self.payload.get("notifType")

        self.data = data

        if self.timestamp:
            self.timestamp = str_to_ts(self.timestamp)


class Session(AminoBaseClass):
    def __init__(self, session: str) -> None:
        self.sid = f"sid={session}"
        self.secret = self.deserialize_session(session)

        self.uid: str = self.secret["2"]
        self.ip: str = self.secret["4"]
        self.created: int = self.secret["5"]
        self.clientType: int = self.secret["6"]

        super().__init__()

    @staticmethod
    def deserialize_session(session: str) -> dict:
        """Takes all the info from a given session

        Parameters
        ----------
        session : str
            the session to deserialize

        Returns
        -------
        dict
            dictionary containing all of the information
        """
        return json.loads(
            urlsafe_b64decode(session + "=" * (4 - len(session) % 4))[1:-20]
        )
