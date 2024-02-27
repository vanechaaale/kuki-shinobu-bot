import os
import interactions

from dotenv import load_dotenv
from apis.enka_api import *
from apis.genshin_api import *
from apis.genshin_dev import *

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = interactions.Intents.DEFAULT
client = interactions.Client(intents=intents, token=TOKEN)

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
    # get all commands
    commands = client._commands
    commands_str = "Commands:\n"
    for command in commands:
        commands_str += f"{command.name}\n"
    await ctx.send(commands_str)

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
                "name": "cookie_token",
                "description": "cookie_token_v2",
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
async def _authenticate(
    ctx: interactions.CommandContext, 
    ltuid: int, 
    ltmid: str, 
    ltoken: str,
    cookie_token: str, 
    uid: int = False):

    # get discord user id
    discord_id = ctx.author.id
    # wait for bot to authenticate

    # defer response
    await ctx.defer()

    auth = await authenticate(discord_id, uid, ltuid, ltmid, ltoken, cookie_token)

    # send response
    await ctx.send(auth)

"""
    Fetch a Genshin player's summary. If no UID is provided, default to author's UID.

    Requirements: Cookies & Authentication Tokens
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
    await ctx.defer()
    summary_str = await get_user_summary(uid, ctx.author.id)
    await ctx.send(summary_str)


"""
    Fetch a Genshin player's character showcase. If no UID is provided, default to author's UID.
    
    Requirements: Cookies & Authentication Tokens

    Parameters:
    uid: int - Optional Genshin player UID. 
"""
@client.command(
        name="showcase",
        description="Show Genshin player's character showcase.",
        options=[
            {
                "name": "uid",
                "description": "Genshin player UID",
                "type": 3,
                "required": False,
            }
        ]
)
async def _showcase(ctx: interactions.CommandContext, uid: int = False):
    await ctx.defer()
    showcase_str = await get_user_showcase(uid, ctx.author.id)
    await ctx.send(showcase_str)


@client.command(
        name="skills",
        description="Display Genshin character information.",
        options=[
            {
                "name": "name",
                "description": "Character name",
                "type": 3,
                "required": True,
            },
            # select skill, passive, or constellations
            {
                "name": "type",
                "description": "Type of skill.",
                "type": 3,
                "required": True,
                "choices": [
                    {
                        "name": "Normal Attack",
                        "value": "na"
                    },
                    {
                        "name": "Elemental Skill",
                        "value": "e_skill"
                    },
                    {
                        "name": "Elemental Burst",
                        "value": "e_burst"
                    },
                    {
                        "name": "Passive",
                        "value": "passive"
                    },
                    {
                        "name": "Constellations",
                        "value": "constellations"
                    }
                ]
            }
        ]
)
async def _skills(ctx: interactions.CommandContext, name: str, type: str):
    formatted_skills = format_char_info(name, type)
    await ctx.send(formatted_skills)

@client.command(
        name="daily",
        description="Claim daily rewards from the HoyoLab website."
)
async def _daily(ctx: interactions.CommandContext):
    success_msg = await claim_daily_rewards(ctx.author.id)
    await ctx.send(success_msg)


@client.command(
        name="redeem",
        description="Redeem Genshin Impact codes.",
        options=[
            {
                "name": "code",
                "description": "Genshin Impact redemption code.",
                "type": 3,
                "required": True,
            }
        ]
)
async def _redeem(ctx: interactions.CommandContext, code: str):
    await ctx.defer()
    success_msg = await redeem_code(code, ctx.author.id)
    await ctx.send(success_msg)

@client.event
async def on_ready():
    # sync commands
    pass

@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {str(error)}")
    
client.start()