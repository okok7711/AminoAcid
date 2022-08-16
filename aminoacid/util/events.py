"""This file is for documentation only, it contains all of the possible events the bot can listen on
"""

from ..abc import Message, Notification


async def on_message(message: Message):
    """This Event will trigger when a new text message is received, it will only be called if the message is not a command

    Parameters
    ----------
    message : Message
        `Message` object describing the message
    """
    ...


async def on_notification(notification: Notification):
    """This Event will trigger when a websocket message with type 10 is received, that is, a new Notification to send to the app

    Parameters
    ----------
    notification : Notification
        `Notification` object describing the notification that was sent
    """
    ...


async def empty_cb(*args, **kwargs):
    """Empty callback for events, this is called when no event callback is defined by the user"""
    ...
