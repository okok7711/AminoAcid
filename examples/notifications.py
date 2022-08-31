from aminoacid import Bot
from aminoacid.util.enums import Topics

client = Bot(
    prefix="b!",
    key=bytes.fromhex("B0000000B50000000000000000000B000000000B"),
    device="42...",
)


@client.event()
async def on_ready():
    await client.socket.subscribe(Topics.ONLINE_MEMBERS.value, ndcId=1)
    print("Ready!!")


client.run(session="AnsiMSI6...")
# OR
# client.run(
#    email      ="mail@gmail.com",
#    password   =   r"Rc2Z;ewjn2jasdn43",
# )
