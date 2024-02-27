import asyncio
import os
import interactions

from enkapy import Enka
from dotenv import load_dotenv
from apis.enka_api import *
from apis.genshin_api import *

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = interactions.Client(token=TOKEN)
enka_client = Enka()

"""
    Display a Help message.
"""
@client.command(
        name="help",
        description="Help commands.",
)
async def _help(ctx: interactions.CommandContext):
    await ctx.send("Implement me...")

"""
    Display a list of all Kuki Bot commands.
"""
@client.command(
        name="commands",
        description="Show list of commands."
)
async def _commands(ctx: interactions.CommandContext):
    await ctx.send("Implement me...")

@client.command(
        name="authenticate",
        description="Set Hoyolab Authentication cookies and Genshin Account UID.",
        options=[
            {
                "name": "ltuid",
                "description": "ltuid_v2",
                "type": 3,
                "required": True,
            },
            {
                "name": "ltmid",
                "description": "ltmid_v2",
                "type": 3,
                "required": True,
            },
            {
                "name": "ltoken",
                "description": "ltoken_v2",
                "type": 3,
                "required": True,
            },  
            {
                "name": "uid",
                "description": "Genshin player UID. (Optional)",
                "type": 3,
                "required": False,
            }
        ]

)
async def _authenticate(ctx: interactions.CommandContext, ltuid: int, ltmid: str, ltoken: str, uid: int = False):
    # get discord user id
    discord_id = ctx.author.id
    # wait for bot to authenticate

    # defer response
    await ctx.defer()

    auth = await authenticate(discord_id, uid, ltuid, ltmid, ltoken)

    # send response
    await ctx.send(auth)

"""
    Fetch a Genshin player's summary. If no UID is provided, default to author's UID.

    Requirements: Cookies & Authentication
"""
@client.command(
        name="summary",
        description="Show Genshin player summary. If no UID is provided, default to author's UID.",
        options=[
            {
                "name": "uid",
                "description": "Genshin player UID",
                "type": 3,
                "required": False,
            }
        ]
)
async def _summary(ctx: interactions.CommandContext, uid: int = False):
    summary_str = await get_user_summary(uid, ctx.author.id)
    await ctx.send(summary_str)

@client.command(
        name="daily",
        description="Claim daily rewards from the HoyoLab website."
)
async def _daily(ctx: interactions.CommandContext):
    success_msg = await claim_daily_rewards(ctx.author.id)
    await ctx.send(success_msg)

@client.event
async def on_ready():
    pass

@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {str(error)}")
    
client.start()