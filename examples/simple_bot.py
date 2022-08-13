from aminoacid import Bot
from aminoacid.abc import Message, Context

client = Bot(
    prefix="b!",
    key=bytes.fromhex("B0000000B50000000000000000000B000000000B"),
    device="42...",
)


@client.command(name="say")
async def hi(ctx: Context, *nya: str):
    message: Message = await ctx.send(" ".join(nya))


@client.event("on_message")
async def on_message(message: Message):
    if message.author.id == client.profile.id:
        return
    print(message)


@client.event()
async def on_ready():
    print(client)


client.run(session="AnsiMSI6...")
# OR
# client.run(
#    email      ="mail@gmail.com",
#    password   =   r"Rc2Z;ewjn2jasdn43",
# )
