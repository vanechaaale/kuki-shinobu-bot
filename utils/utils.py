import interactions

def create_embed(name: str, text: str):
    embed = interactions.Embed(color=0x87cefa)
    embed.add_field(name=f"**{name}**",
                    value=text,
                    inline=False)
    #embed.set_image(url=skin_image_url)
    # embed.set_footer(text="some text"
    return embed