from __future__ import annotations

import asyncio
from time import asctime, time
from typing import TYPE_CHECKING

from aiohttp import ClientConnectorError, ClientWebSocketResponse

from .abc import Message, Notification
from .util import __version__, get_headers, parse_topic
from .util.enums import MessageTypes, NotifTypes, SocketCodes, Topics
from .util.events import empty_cb

if TYPE_CHECKING:
    from . import Bot


class SocketClient:
    """Client for the Amino WebSocket, this receives messages and handles them accordingly"""

    socket: ClientWebSocketResponse

    def __init__(self, client: Bot) -> None:
        self.client = client
        self.http = client._http

    async def run_loop(self):
        """Runs the socket and reconnects every 360 seconds to maintain socket connection"""
        # TODO: make this better i guess?
        await self.run()
        while True:
            await asyncio.sleep(360)
            await self.reconnect()

    async def reconnect(self):
        """Reconnects socket, opens the socket if it didn't open once"""
        if not self.socket.closed:
            await self.socket.close()
        del self.socket
        await self.run()

    async def run(self):
        """Connects to the socket and runs the message handling loop"""
        sign = f"{self.http.device}|{int(time()*1000)}"
        sig = get_headers(data=sign.encode(), key=self.http.key, v=self.http.v)[
            "NDC-MSG-SIG"
        ]
        try:
            self.socket = await self.http.ws_connect(
                url=f"wss://ws1.narvii.com/?signbody={sign}",
                headers={
                    "NDC-MSG-SIG": sig,
                    "NDCDEVICEID": self.http.device,
                    "NDCAUTH": self.http.session.sid,
                    "User-Agent": f"AminoAcid/{__version__} (+https://github.com/okok7711/AminoAcid)",
                },
            )
        except ClientConnectorError as exp:
            self.client.logger.exception(
                f"[{asctime()}] Encountered ClientConnectorError while trying to connect to socket: {exp.strerror}"
            )
            await asyncio.sleep(1)
            return await self.run()
        await (self.client.events.get("on_ready", empty_cb)())
        await self.sock_conn()

    async def handle_message(self, message: Message):
        """Handles received messages
        If it starts with the set prefix, it will handle as command, otherwise it will handle through the on_message event

        Parameters
        ----------
        message : Message
            The message that was received by the socket to handle
        """
        if message.type == MessageTypes.TEXT:
            if not message.startswith(self.client.prefix):
                await (self.client.events.get("on_message", empty_cb)(message))
            else:
                # * Don't handle messages that the bot sends
                if message.author.id == self.client.profile.id:
                    return
                await self.client.handle_command(message)
        else:
            # TODO: Implement other messageTypes
            ...

    async def handle_notification(self, notification: Notification):
        """Handles received notifications
        All unknown or message notifications will cause `on_notification()` to trigger

        Parameters
        ----------
        notification : Notification
            the notification that was received by the socket to handle
        """
        _events = {
            NotifTypes.INVITE_VC.value: "on_vc_invite",
            NotifTypes.START_VC.value: "on_vc_start",
            NotifTypes.MESSAGE.value: "on_notification",
        }
        await (
            self.client.events.get(
                _events.get(notification.type, "on_notification"), empty_cb
            )(notification)
        )

    async def handle_livelayer(self, event: dict):
        """Events that are handled by the livelayer are handled by this

        NOTE: THIS IS STILL VERY MUCH NOT COMPLETE

        Parameters
        ----------
        event : dict
            event data
        """
        _topics = {
            Topics.START_TYPING.value: "on_start_typing",
            Topics.END_RECORDING.value: "on_end_typing",
            Topics.START_RECODING.value: "on_start_recording",
            Topics.END_RECORDING.value: "on_end_recording",
            Topics.ONLINE_MEMBERS.value: "on_online_members",
        }
        await (
            self.client.events.get(
                _topics.get(parse_topic(event["topic"])["topic"], "on_livelayer"),
                empty_cb,
            )(event)
        )

    async def sock_conn(self):
        """While the socket is open, this iterates over all the received messages.
        If it receives a text message, it will go to `self.handle_message` instead.
        """
        async for message in self.socket:
            event = message.json()
            if event["t"] == SocketCodes.MESSAGE:
                message = Message(
                    client=self.client,
                    ndcId=event["o"]["ndcId"],
                    **event["o"]["chatMessage"],
                )
                await self.handle_message(message)
                await self.send(
                    SocketCodes.MESSAGE_ACK,
                    {
                        "ndcId": message.ndcId,
                        "threadId": message.threadId,
                        "messageId": message.id,
                        "markHasRead": True,
                        "createdTime": event["o"]["chatMessage"]["createdTime"],
                    },
                )
            elif event["t"] == SocketCodes.NOTIFICATION:
                await self.handle_notification(Notification(event["o"]))
            elif event["t"] == SocketCodes.LIVE_LAYER_USER_JOINED_EVENT:
                await self.handle_livelayer(event["o"])
            else:
                self.client.logger.info(
                    f"[{asctime()}] Socket sent unhandled message: {message}"
                )

    async def send(self, code: int, obj: dict):
        self.client.logger.info(f"[{asctime()}] Sending Message to socket: {obj}")
        await self.socket.send_json(
            {"t": code, "o": {"id": str(round(time() % 86400)), **obj}}
        )

    async def subscribe(self, topic: str, *, ndcId: str = ""):
        topic = f"ndtopic:g:{topic}" if not ndcId else f"ndtopic:x{ndcId}:{topic}"
        await self.send(
            SocketCodes.SUBSCRIBE_LIVE_LAYER_REQUEST,
            {"topic": topic, "ndcId": ndcId},
        )

    async def unsubscribe(self, topic: str, *, ndcId: str = ""):
        topic = f"ndtopic:g:{topic}" if not ndcId else f"ndtopic:x{ndcId}:{topic}"
        await self.send(
            SocketCodes.UNSUBSCRIBE_LIVE_LAYER_REQUEST,
            {"topic": topic, "ndcId": ndcId},
        )
