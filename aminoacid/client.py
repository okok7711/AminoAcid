from abc import ABC
from time import time
from typing import Optional

from . import exceptions
from .abc import Member, Message, Thread, User, Embed


class ApiClient(ABC):
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
            exceptions.handle_exception(response.get("api:statuscode"), response)

        self.profile = User(**response, client=self)
        self._http.session = f"sid={response.get('sid')}"

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
            exceptions.handle_exception(response.get("api:statuscode"), response)
        return Thread(**(response["thread"]), client=self)

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
            exceptions.handle_exception(response.get("api:statuscode"), response)
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
        # TODO: Maybe add @overload to fetch_user instead of defining the exact same method twice
        response = await (
            await self._http.request("GET", f"/x{ndcId}/s/user-profile/{userId}")
        ).json()

        if response.get("api:statuscode") != 0:
            exceptions.handle_exception(response.get("api:statuscode"), response)

        return Member(**(response["userProfile"]), client=self)

    async def send_message(
        self,
        threadId: str,
        content: str,
        *,
        ndcId: Optional[str] = "",
        embed: Optional[Embed] = ...,
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
            Embed to send alongside the message, by default ...
            **THIS IS NOT IMPLEMENTED YET**

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
                    **kwargs,
                },
            )
        ).json()

        if response.get("api:statuscode") != 0:
            exceptions.handle_exception(response.get("api:statuscode"), response)
        return Message(**(response["message"]), client=self)
