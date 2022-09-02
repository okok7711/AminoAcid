from aminoacid import Bot
from aminoacid.abc import Message, Context
from aminoacid.exceptions import AminoBaseException

client = Bot(
    prefix="b!",
    key=bytes.fromhex("B0000000B50000000000000000000B000000000B"),
    device="42...",
)


@client.command(name="say")
async def hi(ctx: Context, *nya: str):
    await ctx.reply(" ".join(nya))


@client.command(cooldown=1440 * 60)
async def claim(ctx: Context):
    blogs = await ctx.author.fetch_blogs()
    if not blogs:
        return await ctx.reply("You don't have any blogs!")
    await blogs[0].tip(100)
    await ctx.reply("Check in tmrw again!!")


@claim.error()
async def claim_error(exc: AminoBaseException, ctx: Context):
    await ctx.send(f"An error occurred: {exc}")


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
