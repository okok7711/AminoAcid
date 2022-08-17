**This project is in no way associated with Amino or MediaLabs, this is completely reverse engineered**

# AminoAcid

## Why AminoAcid?
Because other projects like [BotAmino](https://github.com/vedansh5/BotAmino) fail to allow a nicely done, pythonic, completely async hinted experience.  
This project aims to open up the possibilities that other libraries don't fulfill by being completely async using aiohttp, allowing OOP, allowing [events](https://okok7711.github.io/AminoAcid/aminoacid/util/events.html) with a discord.py-esque experience.  
While BotAmino *tries* to be easy to use it fails to provide an easy high-level API by forcing to use [Amino.fix](https://github.com/Minori101/Amino.fix) instead of allowing access via their own methods and objects.

## How do you use it?
AminoAcid's documentation is available through [GitHub pages](https://okok7711.github.io/AminoAcid/aminoacid.html) and auto generated using [pdoc](https://github.com/mitmproxy/pdoc/), for examples take a look into [the examples dir](/examples)  
```python
from aminoacid import Bot
from aminoacid.abc import Message, Context

client = Bot(
    prefix="b!",
    key=bytes.fromhex("B0000000B50000000000000000000B000000000B"),
    device = "42..."
)

@client.command(name="say")
async def hi(ctx: Context, *nya: str):
    message = await ctx.send(" ".join(nya))
    print(message)

@client.event("on_message")
async def on_message(message: Message):
    if message.author.id == client.profile.id: return
    print(message, "nya!")

client.run(
    session="AnsiMSI6..."
)
# OR
#client.run(
#    email="mail@gmail.com",
#    password=   r"Rc2Z=I5S0bN;ewjn2jasdn43",
#)
```
As you might see, you need to supply your own key to sign the requests with. You can find this in other libraries tho.  
Please note, that this library is **NOT** finished and a lot of features I want to implement are still missing.

## How to subscribe to topics to get notifications?
AminoAcid supports receiving notification events via the socket like the normal app would.  
The notification future still needs a lot of work, because so far it's not receiving events like follow, comment, etc.  

To receive notifications with a certain topic you can it's suggested to send a subscribe object in your on_ready callback
```python
...

@client.event()
async def on_ready():
    client.logger.info(client._http.session)
    await client.socket.subscribe(ndcId, topic=topic)

...
```
so far known topics are documented in 

## Why no key?
The aim of this library is **NOT** to make malicious bots, which is why you need to put the key in yourself.  
This library should only be used for making fun chat bots.

## How to do X?
Check the docs, if it's in there then look at how to use it. If it's not there you probably can't.  
If you want to request a feature, you can open a new Issue.

## AminoAcid or AminoAcids?
This was originally called AminoAcids but then i noticed that the pypi project "aminoacids" was already taken, so i removed the s

## To-Do
- [ ] Finish Object attributes
- [ ] Type checking and converting
- [x] Add Embed features
- [ ] Improve existing features
- [ ] Better quality in code
- [ ] Complete Exceptions
- [x] Complete SocketCode Enum
- [x] Make the SocketClient subscribe to other events to allow on_follow and on_notification events 
- [x] Finish started but unfinished methods
- [ ] Cog-like Command categories
- [ ] on_typing_start, etc. events (socket code 400)