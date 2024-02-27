import random
import interactions
from interactions import Button, ButtonStyle

from utils.constants import VISION_TO_COLOR

def create_embed(
        name: str, 
        text: str, 
        icon: str = None, 
        color : str = None,
        page: int = None,
        total_pages: int = None,
        title: str = None
        ):
    vision_colors = VISION_TO_COLOR.values()
    embed = interactions.Embed(
        color=color if color else random.choice(list(vision_colors)),
        title=title if title else "Title",
        )
    embed.add_field(
        name=name,
        value=text,
        inline=False)
    embed.set_thumbnail(url=icon)
    embed.set_footer(text=f"Page {page} of {total_pages}" if page and total_pages else f"Page 1 of 1")
    return embed

def create_page_buttons():
    buttons = []
    prev = Button(
        style=ButtonStyle.SECONDARY,
        label="prev",
        custom_id="prev_page",
    )
    next = Button(
        style= ButtonStyle.PRIMARY,
        label="next",
        custom_id="next_page",
    )
    buttons.append(prev)
    buttons.append(next)
    return buttons