"""This file is for documentation only, it contains all of the possible events the bot can listen on
"""

from ..abc import Message, Notification

from logging import getLogger

logger = getLogger(__name__)


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


async def on_vc_start(notification: Notification):
    """This Event will trigger when the socket receives a new Event containing notifType 31
    containing data will look like this:
    ```json
    {"payload": {
        "uid": "00000000-0000-0000-0000-000000000000",
        "notifType": 31,
        "aps": {
            "badge": 1,
            "alert":
            "person started Live Mode in Private Chat"
            },
        "community": {
            "name": "...",
            "icon": "http://cm1.narvii.com/..."
            },
        "exp": 1660740937,
        "ndcId": 0,
        "tid": "00000000-0000-0000-0000-000000000000",
        "ttype": 0,
        "id": "00000000-0000-0000-0000-000000000000",
        "userProfile": {
            ...
            }
    }}
    ```

    Parameters
    ----------
    notification : Notification
        `Notification` object describing the vc start notification that was received
    """
    ...


async def on_vc_invite(notification: Notification):
    """This Event will trigger when the socket receives a new Event containing notifType 29
    containing data has the same format as `on_vc_start()`

    Parameters
    ----------
    notification : Notification
        `Notification` object describing the vc invite
    """
    ...


async def on_start_typing(event: dict):
    """Event for when a user starts typing in a given chat
    `event` structure:
    ```json
    {
        "topic": "ndtopic:x1:users-start-typing-at:00000000-0000-0000-0000-000000000000",
        "ndcId": 1,
        "userProfileCount": 1,
        "userProfileList": [
            {
                ...
            }
        ]
    }
    ```

    Parameters
    ----------
    event : dict
        the event that was sent
    """
    ...


async def on_end_typing(event: dict):
    """Same as `on_start_typing()` only that this is for when the user stops typing

    Parameters
    ----------
    event : dict
        the event that was sent
    """
    ...


async def on_start_recording(event: dict):
    """Same as `on_start_typing()` only that this is for when the user starts recording a vm

    Parameters
    ----------
    event : dict
        the event that was sent
    """
    ...


async def on_end_recording(event: dict):
    """Same as `on_start_typing()` only that this is for when the user stops recording a vm

    Parameters
    ----------
    event : dict
        the event that was sent
    """
    ...


async def on_online_members(event: dict):
    """Event triggered when a user comes online and joins the livelayer

    NOTE: Currently subscribing to the livelayer is very weird and this event doesn't always get triggered,
    if you want to help with research please DM me on discord (okok#7711)!!

    Structure:
    ```json
    {
        "topic": "ndtopic:x1:online-members",
        "ndcId": 1,
        "userProfileCount": 1,
        "userProfileList": [
            {
                ...
            }
        ]
    }
    ```

    Parameters
    ----------
    event : dict
        the event that was sent
    """
    ...


async def empty_cb(*args, **kwargs):
    """Empty callback for events, this is called when no event callback is defined by the user"""
    logger.info(f"{args, kwargs}")
