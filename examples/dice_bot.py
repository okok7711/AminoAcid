from aminoacid import Bot
from aminoacid.abc import Message, Context

import random

client = Bot(
    prefix="b!",
    key=bytes.fromhex("B0000000B50000000000000000000B000000000B"),
    device="42...",
)


@client.command()
async def roll(ctx: Context, *nya: str):
    await ctx.send()


@client.event()
async def on_ready():
    print("Ready!")


client.run(session="AnsiMSI6...")
# OR
# client.run(
#    email      ="mail@gmail.com",
#    password   =   r"Rc2Z;ewjn2jasdn43",
# )