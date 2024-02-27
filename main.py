import os
import interactions

from dotenv import load_dotenv
from apis.enka_api import *
from apis.genshin_api import *
from apis.genshin_dev import *
from utils.utils import *
from interactions import Button, ButtonStyle, Client, CommandContext, Component, ComponentContext, Intents

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = Intents.DEFAULT
client = Client(intents=intents, token=TOKEN)

"""
    Display a Help message.
"""
@client.command(
        name="help",
        description="Help commands.",
)
async def _help(ctx: CommandContext):
    embed = create_embed(ctx.command.name, "Help message.")
    await ctx.send(embeds=embed)

"""
    Display a list of all Kuki Bot commands.

    Sends:
    str - List of commands in an Embed Message.
"""
@client.command(
        name="commands",
        description="Show list of commands."
)
async def _commands(ctx: CommandContext):
    commands = client._commands
    commands_str = "All available commands:\n\n"
    for command in commands:
        commands_str += f"**/{command.name}:** " + f"{command.description}\n\n"
    embed = create_embed(ctx.command.name, commands_str)
    await ctx.send(embeds=embed)

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
    ctx: CommandContext, 
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

    Parameters:
    uid: int - Optional Genshin player UID.

    Sends:
    Embed - 3 Page Embed Message containing Genshin player summary.
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
async def _summary(ctx: CommandContext, uid: int = False):
    await ctx.defer()
    summary_str = await get_genshin_api_user_summary(ctx.author.id, uid)
    await ctx.send(summary_str)


"""
    Fetch a Genshin player's character showcase. If no UID is provided, default to author's UID.
    
    Requirements: Cookies & Authentication Tokens

    Parameters:
    uid: int - Optional Genshin player UID. 

    Sends:
    str - Genshin player character showcase string.
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
async def _showcase(ctx: CommandContext, uid: int = False):
    await ctx.defer()
    # get list of showcased character's embeds
    showcases = await get_user_showcase(uid, ctx.author.id)
    
    buttons = []

    # I think the emojis are kinda ugly with the button ngl
    prev = Button(
        style=ButtonStyle.SECONDARY,
        label="prev",
        custom_id="prev_showcase",
        # emoji=interactions.Emoji(name="⬅️")
    )
    next = Button(
        style= ButtonStyle.PRIMARY,
        label="next",
        custom_id="next_showcase",
        # emoji=interactions.Emoji(name="➡️")
    )
    buttons.append(prev)
    buttons.append(next)

    # Send first showcase
    interaction = await ctx.send(embeds=showcases[0], components=[buttons])

        
    @client.event
    async def on_component(ctx: ComponentContext):
        # get index of current showcase
        for i, embed in enumerate(showcases):
            if embed.fields[0].name in ctx.message.embeds[0].fields[0].name:
                idx = i
                break
        if ctx.custom_id == "next_showcase":
            idx = idx + 1 if idx < len(showcases) - 1 else 0
            await ctx.edit(embeds=showcases[idx], components=[buttons])
        elif ctx.custom_id == "prev_showcase":
            idx -= 1 if idx >= 0 else len(showcases) - 1
            await ctx.edit(embeds=showcases[idx], components=[buttons])
        
    
"""
    Fetch the author's notes (realm currency, resin, comissions, and expeditions). 

    Requirements: Cookies & Authentication Tokens

    Errors: 
    [10102] Cannot view real-time notes of other users.

    Sends:
    Embed - Genshin player notes in an Embed message.
"""
@client.command(
        name="notes",
        description="Show Genshin player's notes."
)
async def _notes(ctx: CommandContext):
    await ctx.defer()
    notes_str = await get_notes(ctx.author.id)
    await ctx.send(notes_str)

@client.command(
        name="books",
        description="Display Genshin character talent books for the day."
)
async def _books(ctx: CommandContext):
    books_str = format_daily_talent_books()
    await ctx.send(books_str)

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
async def _skills(ctx: CommandContext, name: str, type: str):
    formatted_skills = format_char_info(name, type)
    await ctx.send(formatted_skills)

@client.command(
        name="daily",
        description="Claim daily rewards from the HoyoLab website."
)
async def _daily(ctx: CommandContext):
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
async def _redeem(ctx: CommandContext, code: str):
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