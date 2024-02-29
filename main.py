import os

from dotenv import load_dotenv
from apis.enka_api import *
from apis.genshin_api import *
from apis.genshin_dev import *
from utils.utils import *
from interactions import Client, CommandContext, ComponentContext, Intents, LibraryException
from utils.constants import EMOJIS_TO_ID, CharacterSkills

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

    # Send first showcase
    interaction = await ctx.send(embeds=showcases[0], components=[buttons])
    buttons = create_page_buttons(custom_id=interaction.id)
    await ctx.edit(embeds=showcases[0], components=[buttons])
    
    """
        Event listener for the showcase buttons.
    """
    @client.event
    async def on_component(ctx: ComponentContext):
        await handle_page_buttons(ctx, buttons, int(interaction.id), showcases)

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
    # Get Emojis ids for the embed
    notes_embed = await get_notes_embed(ctx.author.id)
    await ctx.send(embeds=notes_embed)

@client.command(
        name="books",
        description="Display Genshin character talent books for the day."
)
async def _books(ctx: CommandContext):
    # List of available talent books as embeds
    embeds = get_daily_talent_books_embeds()
    buttons = []

    await ctx.defer()
    interaction = await ctx.send(embeds=embeds[0], components=[buttons])
    buttons = create_page_buttons(custom_id=interaction.id)
    await ctx.edit(embeds=embeds[0], components=buttons)
    
    """
        Event listener for the talent book buttons.
    """
    @client.event
    async def on_component(ctx: ComponentContext):
        await handle_page_buttons(ctx, buttons, int(interaction.id), embeds, compareName=True)

        
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
            # select combat skills, passive, or constellations
            {
                "name": "type",
                "description": "Type of skill.",
                "type": 3,
                "required": True,
                "choices": [
                    {
                        "name": CharacterSkills.NORMAL_ATTACK.value,
                        "value": CharacterSkills.NORMAL_ATTACK.value
                    },
                    {
                        "name": CharacterSkills.ELEMENTAL_SKILL.value,
                        "value": CharacterSkills.ELEMENTAL_SKILL.value
                    },
                    {
                        "name": CharacterSkills.ELEMENTAL_BURST.value,
                        "value": CharacterSkills.ELEMENTAL_BURST.value
                    },
                    {
                        "name": CharacterSkills.PASSIVE_TALENTS.value,
                        "value": CharacterSkills.PASSIVE_TALENTS.value
                    },
                    {
                        "name": CharacterSkills.CONSTELLATIONS.value,
                        "value": CharacterSkills.CONSTELLATIONS.value
                    }
                ]
            }
        ]
)
async def _skills(ctx: CommandContext, name: str, type: str):
    components=[]
    await ctx.defer()
    embeds, scalings = embed_char_skill_info(name, type)
    interaction = await ctx.send(embeds=embeds[0], components=components)
    # Normal Attack, Elemental Skill, Elemental Burst have a Show Details button
    if (type == CharacterSkills.NORMAL_ATTACK.value or
        type == CharacterSkills.ELEMENTAL_SKILL.value or
        type == CharacterSkills.ELEMENTAL_BURST.value) and scalings:
        buttons = create_page_buttons(custom_id=interaction.id)
        components.append(buttons)
        await ctx.edit(embeds=embeds[0], components=components)
    """
        Event listener for the Show Details button on Character skills message.
    """
    @client.event
    async def on_component(ctx: ComponentContext):
        await handle_page_buttons(ctx, buttons, int(interaction.id), embeds, compareName=True)

@client.command(
        name="daily",
        description="Claim daily rewards from the HoyoLab website."
)
async def _daily(ctx: CommandContext):
    try:
        success_msg = await claim_daily_rewards(ctx.author.id)
        await ctx.send(success_msg)
    except genshin.AlreadyClaimed:
        # Catch api error when trying to claim daily rewards again
        await ctx.send(genshin.AlreadyClaimed.msg)


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
    # handle command errors
    print(error)
    await ctx.send(str(error))

client.start()