import random
import interactions
from interactions import Button, ButtonStyle, CommandContext, ComponentContext, Interaction

from utils.constants import VISION_TO_COLOR

def create_embed(
        name: str, 
        text: str, 
        icon: str = None, 
        color : str = None,
        page: int = None,
        total_pages: int = None,
        title: str = None,
        ):
    vision_colors = VISION_TO_COLOR.values()
    embed = interactions.Embed(
        color=color if color else random.choice(list(vision_colors)),
        title=title if title else "Title",
        )
    text1 = None
    text2 = None
    if len(text) > 1024:
        # split text into 2 fields
        text1 = text[:1024]
        text2 = text[1024:]
    embed.add_field(
        name=name,
        value=text1 if text1 else text,
        inline=False)
    if text2:
        embed.add_field(
            name=" ",
            value=text2,
            inline=False)
    embed.set_footer(text=f"Page {page} of {total_pages}" if page and total_pages else f"Page 1 of 1")
    return embed

def create_page_buttons(custom_id: int):
    buttons = []
    prev = Button(
        style=ButtonStyle.SECONDARY,
        label="prev",
        custom_id=str(custom_id),
    )
    next = Button(
        style= ButtonStyle.PRIMARY,
        label="next",
        custom_id=str(int(custom_id) + 1),
    )
    buttons.append(prev)
    buttons.append(next)
    return buttons

def create_show_details_button():
    more_details = Button(
        style=ButtonStyle.PRIMARY,
        label="Show Details",
        custom_id="show_details",
    )
    return more_details

async def handle_page_buttons(ctx: ComponentContext, 
                              buttons, 
                              interaction_id: int, 
                              embeds, 
                              compareName=False):
    idx = 0
    # get current idx
    for i, embed in enumerate(embeds):
        if compareName:
            c1 = embed.fields[0].name
            c2 = ctx.message.embeds[0].fields[0].name
        else:
            c1 = embed.title
            c2 = ctx.message.embeds[0].title
        if c1 == c2:
            idx = i
            break
    # prev
    if str(ctx.custom_id) == str(interaction_id):
        idx = idx - 1 if idx > 0 else len(embeds) - 1
        await ctx.edit(embeds=embeds[idx], components=buttons)
    # next
    elif str(ctx.custom_id) == str(interaction_id + 1):
        idx = idx + 1 if idx < len(embeds) - 1 else 0
        await ctx.edit(embeds=embeds[idx], components=buttons)
    else:
        return
