from os import PathLike
from time import time
from typing import BinaryIO, List, Optional, Union

from . import exceptions
from .abc import (
    AminoBaseClass,
    Embed,
    Member,
    Message,
    Session,
    Thread,
    User,
    Community,
)


class ApiClient(AminoBaseClass):
    """ApiClient skeleton to reduce repeating API calls in code and to clean up code"""

    async def login(self, email: str, password: str) -> User:
        """Authenticates with the given email and password

        Parameters
        ----------
        email : str
            Email to login with
        password : str
            Password to login with

        Returns
        -------
        User
            The user that was authenticated
        """
        response = await (
            await self._http.request(
                "POST",
                "/g/s/auth/login",
                json={
                    "email": email,
                    "v": 2,
                    "secret": f"0 {password}",
                    "deviceID": self._http.device,
                    "clientType": 100,
                    "action": "normal",
                    "timestamp": int(time() * 1000),
                },
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)

        self.profile = User(**(response["userProfile"]), client=self)
        self._http.session = Session(response.get("sid"))

        return self.profile

    async def fetch_thread(self, threadId: str, ndcId: Optional[str] = "") -> Thread:
        """Fetches a given `Thread`

        Parameters
        ----------
        threadId : str
            the ID of the thread
        ndcId : Optional[str], optional
            the community the thread is in, if not given (or 0) it will look for the thread in global, by default ""

        Returns
        -------
        Thread
            The `Thread` object that was requested
        """
        response = await (
            await self._http.request(
                "GET",
                f"/x{ndcId}/s/chat/thread/{threadId}"
                if ndcId
                else f"/g/s/chat/thread/{threadId}",
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)
        return Thread(**(response["thread"]), client=self)

    async def fetch_message(
        self, messageId: str, threadId: str, ndcId: Optional[str] = ""
    ) -> Message:
        """Fetches a given `Message` from a `Thread`

        Parameters
        ----------
        messageId : str
            the ID of the `Message` to fetch
        threadId : str
            the ID of the `Thread` to fetch from
        ndcId : Optional[str], optional
            the community the thread is in, if not given (or 0) it will look for the thread in global, by default, by default ""

        Returns
        -------
        Message
            The `Message` object that was requested
        """
        response = await (
            await self._http.request(
                "GET",
                f"/x{ndcId}/s/chat/thread/{threadId}/message/{messageId}"
                if ndcId
                else f"/g/s/chat/thread/{threadId}/message/{messageId}",
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)
        return Thread(**(response["message"]), client=self)

    async def fetch_user(self, userId: str) -> User:
        """Fetches a user from the API

        Parameters
        ----------
        userId : str
            the userId to search for

        Returns
        -------
        User
            The `User` object that was requested
        """
        response = await (
            await self._http.request("GET", f"/g/s/user-profile/{userId}")
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)
        return User(**(response["userProfile"]), client=self)

    async def fetch_member(self, userId: str, ndcId: str) -> Member:
        """Fetches a member for a given community

        Parameters
        ----------
        userId : str
            The userId to search for
        ndcId : str
            The community the user is a member in

        Returns
        -------
        Member
            The `Member` object requested for the given community
        """
        response = await (
            await self._http.request("GET", f"/x{ndcId}/s/user-profile/{userId}")
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)

        return Member(**(response["userProfile"]), client=self)

    async def send_message(
        self,
        threadId: str,
        content: str,
        *,
        ndcId: Optional[str] = "",
        embed: Optional[Embed] = Embed(None, None, None, None, None, None),
        **kwargs,
    ) -> Message:
        """Sends a message to a given Thread.

        Parameters
        ----------
        threadId : str
            the thread to send the message to
        content : str
            the content of the message to send, must be within 2000 characters
        ndcId : Optional[str], optional
            The community the Thread is in, if not given (or 0) it will look for a global chat, by default ""
        embed : Optional[Embed], optional
            Embed to send alongside the message, by default empty embed

        Returns
        -------
        Message
            Returns the `Message` object of the sent message
        """
        response = await (
            await self._http.request(
                "POST",
                f"/x{ndcId}/s/chat/thread/{threadId}/message"
                if ndcId
                else f"/g/s/chat/thread/{threadId}",
                json={
                    "type": 0,
                    "content": content,
                    "clientRefId": int(time() % 86400),
                    "timestamp": int(time() * 1000),
                    "attachedObject": embed.__dict__(),
                    **kwargs,
                },
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)
        return Message(**(response["message"]), client=self)

    async def start_dm(self, userId: str, *, ndcId: Optional[str] = "") -> Thread:
        """Start direct messaging a user or return the Thread if a DM already exists

        Parameters
        ----------
        userId : str
            the user you want to start a DM with
        ndcId : Optional[str], optional
            the community the member is in, if sending to a user, this  will be empty

        Returns
        -------
        Thread
            Thread of the DMs
        """
        response = await (
            await self._http.request(
                "POST",
                f"/x{ndcId}/s/chat/thread/" if ndcId else f"/g/s/chat/thread/",
                json={
                    "title": None,
                    "content": None,
                    "initialMessageContent": None,
                    "timestamp": int(time() * 1000),
                    "inviteeUids": [userId],
                    "type": 0,
                },
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)

        return Thread(**(response["thread"]), client=self)

    async def message_user(self, userId: str, **kwargs) -> Message:
        """Send a message to a user's DMs, this starts the DMs (via `start_dm()`) if they don't exist already

        Parameters
        ----------
        userId : str
            userId to send a message to

        Returns
        -------
        Message
            Return an object representing the sent message
        """
        return await (
            await self.start_dm(userId=userId, ndcId=kwargs.pop("ndcId", ""))
        ).send(**kwargs)

    async def upload_image(self, image: Union[bytes, BinaryIO, PathLike]) -> str:
        """Upload an image to the amino servers

        Parameters
        ----------
        image : Union[bytes, BinaryIO, PathLike]
            Either the read out image, an IO object representing the Image, or the image path

        Returns
        -------
        str
            The direct link of the image
        """
        if isinstance(image, (BinaryIO, PathLike)):
            kwargs = {"file": image}
        else:
            kwargs = {"data": image}
        response = await (
            await self._http.request("POST", "/g/s/media/upload", **kwargs)
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)

        return response["mediaValue"]

    async def set_device(self, ndcId: str = "") -> Optional[dict]:
        """Set the device pushToken to receive notifications on the websocket

        Parameters
        ----------
        ndcId : str, optional
            Optionally a community to set the token in, by default ""

        Returns
        -------
        Optional[dict]
            A dictionary containing devOptions, returns None if it doesn't exist
        """
        response = await (
            await self._http.request(
                "POST",
                f"/x{ndcId}/s/device" if ndcId else "/g/s/device",
                json={
                    "deviceID": self._http.device,
                    "bundleID": "com.narvii.amino.master",
                    "clientType": 100,
                    "timezone": 60,
                    "systemPushEnabled": True,
                    "locale": "en_DE",
                    "deviceToken": self._http.token,
                    "deviceTokenType": 1,
                    "timestamp": int(time() * 1000),
                },
            )
        ).json()
        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)

        return response["devOptions"]

    async def fetch_communities(
        self, start: int = 0, size: int = 25
    ) -> List[Community]:
        """Fetch a list of communities that the bot is in, this can be used to set tokens for each community

        Parameters
        ----------
        start : int, optional
            start index, by default 0
        size : int, optional
            amount of communities to fetch, by default 25

        Returns
        -------
        List[Community]
            List of `Community` objects describing the communities
        """
        response = await (
            await self._http.request(
                "GET", "/g/s/community/joined", params={"start": start, "size": size}
            )
        ).json()

        if response.get("api:statuscode") != 0:
            return exceptions.handle_exception(response.get("api:statuscode"), response)
        return [
            Community(**community, client=self)
            for community in response["communityList"]
        ]
