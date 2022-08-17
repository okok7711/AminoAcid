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

async def empty_cb(*args, **kwargs):
    """Empty callback for events, this is called when no event callback is defined by the user"""
    ...
