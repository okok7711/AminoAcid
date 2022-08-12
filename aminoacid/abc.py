from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Callable, Optional, overload, Union

if TYPE_CHECKING:
    from . import Bot


class AminoBaseClass(ABC):
    """This is the base class for all other classes defined by this library, except for clients and exceptions."""

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        _temp = [
            f"{attr}={value!r}, "
            for attr, value in vars(self).items()
            if value and not isinstance(value, (Callable, type(self.client)))
        ]
        return f"{type(self).__name__}({''.join(_temp)})"


class MessageAble(ABC):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__()

    @overload
    async def send(
        self: Union[Member, User], content: str, *, embed=..., url: str = ""
    ) -> Message:
        """Send a Message to the User

        Parameters
        ----------
        content : str
            Content of the message, cannot be empty, must be within 2000 character
        embed : Embed, optional
            The embed to send alongside the message, by default ...

        Returns
        -------
        Message
            Message object of the sent message
        """

        # TODO: Finish sending messages to User/Member object.
        return self.client.send_message(self)

    async def send(self, content: str, *, embed=..., url: str = "") -> Message:
        """Send a Message to the Channel

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
                content=content, threadId=self.threadId, ndcId=self.ndcId
            )
        if isinstance(self, Context):
            return await self.client.send_message(
                content=content,
                threadId=self.message.threadId,
                ndcId=self.message.ndcId,
            )
        if isinstance(self, Thread):
            return await self.client.send_message(
                content=content, threadId=self.id, ndcId=self.ndcId
            )


class Context(MessageAble):
    """Context of a message, this is passed into `UserCommand`s as the first positional argument"""

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

    async def reply(self, content: str, **kwargs):
        """Replies to the message described by the context (`self.message`)

        Parameters
        ----------
        content : str
            Content of the message to reply with
        """
        if self.message.ndcId:
            url = f"/x{self.message.ndcId}/s/chat/thread/{self.thread.id}"
        else:
            f"/g/s/chat/thread/{self.thread.id}"
        await super().send(content, url=url**kwargs, replyMessageId=self.message.id)


class User(MessageAble, AminoBaseClass):
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
        """Initialises a new `User` object, calls `_from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `User` with, by default {}
        """
        self._from_dict({**data, **kwargs})
        super().__init__(bot=self.client)

    def _from_dict(self, data: dict):
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

    async def send(self, content: str, *, embed=...) -> Message:
        # TODO: Implement this, and allow sending Messages via User Object
        url = f"/g/s/chat/thread"
        return await super().send(content, embed=embed, url=url)

    async def get(self):
        """Get the complete `User` object, used when a `User` is received partially by the socket to get the missing information."""
        # TODO: Implement this, use `fetch_user` defined in ApiClient
        ...


class Member(User):
    ndcId: int

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Member` object, calls `_from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Member` with, by default {}
        """
        self._from_dict({**data, **kwargs})
        super().__init__(data, **kwargs)

    def _from_dict(self, data: dict):
        """Create a new `Member` object from a dict

        Parameters
        ----------
        data : dict
            The dict to create the new `Member` object from
        """
        self.ndcId = data.pop("ndcId")
        return super()._from_dict(data)

    async def send(self, content: str, *, embed=...) -> Message:
        # TODO: Same as User.
        return await super().send(content, embed=embed)


class Message(AminoBaseClass):
    id: str
    type: int
    content: str
    author: User
    threadId: str
    ndcId: Optional[int] = None
    isHidden: bool
    includedInSummary: bool
    createdTime: str
    extensions: dict
    alertOption: int
    membershipStatus: int
    chatBubbleId: str
    chatBubbleVersion: int
    clientRefId: int
    mediaType: int

    client: Bot

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Message` object, calls `_from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Message` with, by default {}
        """
        self._from_dict({**data, **kwargs})
        super().__init__()
        self.startswith = self.content.startswith

    def _from_dict(self, data: dict):
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

        self.createdTime = data.pop("createdTime", "")
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
            # TODO: Yea, also need to implement this.
            ...


class Thread(MessageAble, AminoBaseClass):
    id: str
    content: str
    author: User
    ndcId: Optional[int] = None
    title: str

    def __init__(self, data: dict = {}, **kwargs) -> None:
        """Initialises a new `Thread` object, calls `_from_dict()` with a combination of the kwargs and the supplied data

        Parameters
        ----------
        data : dict, optional
            The data to initialise the `Thread` with, by default {}
        """
        self._from_dict({**data, **kwargs})
        super().__init__(bot=self.client)

    def _from_dict(self, data: dict):
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

    async def send(content: str, *, embed: ..., url: str) -> Message:
        return await super().send(content, embed=embed, url=url)

    async def get(self):
        """Get the complete `Thread` object, used when a `Thread` is received partially by the socket to get the missing information."""
        self._from_dict(
            (await self._bot.get_thread(ndcId=self.ndcId, threadId=self.id)).__dict__
        )


class Embed(AminoBaseClass):
    # TODO: Add Embed classes for both image embeds and user embeds.
    ...


class Frame(AminoBaseClass):
    # TODO: Add Frame class for OOP
    ...
