from __future__ import annotations
import asyncio

from time import time
from typing import TYPE_CHECKING

from aiohttp import ClientWebSocketResponse

from .util import get_headers, __version__
from .util.enums import SocketCodes, MessageTypes
from .abc import Message

if TYPE_CHECKING:
    from . import Bot


async def empty_cb(*args, **kwargs):
    """Empty callback for events, this is called when no event callback is defined by the user"""
    ...


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
        """Reconnects socket, opens the socket if it didn't open once

        Returns
        -------
        None
            returns if the socket hasn't been opened yet, which case the socket will open first
        """
        if "socket" not in dir(self):
            return await self.run()
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
        self.socket = await self.http.ws_connect(
            url=f"wss://ws1.narvii.com/?signbody={sign}",
            headers={
                "NDC-MSG-SIG": sig,
                "NDCDEVICEID": self.http.device,
                "NDCAUTH": self.http.session,
                "User-Agent": f"AminoAcid/{__version__} (+https://github.com/okok7711/AminoAcids)",
            },
        )
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
                await self.client.events["on_message"](message)
            else:
                await self.client.handle_command(message)
        else:
            print(message)

    async def sock_conn(self):
        """While the socket is open, this iterates over all the received messages.
        If it receives a text message, it will go to `self.handle_message` instead.
        """
        await (self.client.events.get("on_ready", empty_cb)())
        async for message in self.socket:
            event = message.json()
            if event["t"] == SocketCodes.MESSAGE:
                await self.handle_message(
                    Message(
                        client=self.client,
                        ndcId=event["o"]["ndcId"],
                        **event["o"]["chatMessage"],
                    )
                )
