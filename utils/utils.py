import interactions

def create_embed(
        name: str, 
        text: str, 
        icon: str = None, 
        color : str = None,
        page: int = None,
        total_pages: int = None
        ):
    embed = interactions.Embed(
        color=color if color else "black",
        title=name,
        )
    embed.add_field(
        name="Details:",
        value=text,
        inline=False)
    embed.set_thumbnail(url=icon)
    embed.set_footer(text=f"Page {page} of {total_pages}" if page and total_pages else f"Page 1 of 1")
    return embed