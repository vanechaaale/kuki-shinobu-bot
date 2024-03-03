"""
    Fetch a Genshin player's summary. If no UID is provided, default to author's UID.

    Parameters:
        uid: int - Genshin player UID

    Returns:
        str - Genshin player summary string containing, UID, Nickname, Level, Signature, and Abyss floor
"""
async def get_enka_user_summary(discord_id: int, uid: int = False):
    # If UID is not provided, look for the author's UID
    await client.load_lang()

    if not uid:
        user = get_user_from_db(discord_id)
        uid = user['uid']
        # If no uid was found, the discord user has not linked their own genshin uid yet.

    user = await client.fetch_user(uid)
    nameCardId = user.player.nameCardId
    avatarId = user.player.profilePicture.avatarId
    summary_f1 = []
    summary_f2 = []

    # case for unknown characters in username (looking at you, Greg)
    try: 
        title = user.player.nickname
        summary_f1.append(f"UID: `{uid}`\n")
    except UnicodeEncodeError:
        title = f"Player {str(uid)}"
        
    summary_f1.append(f"Level: `{user.player.level}`\n Signature: `{user.player.signature}`\n")
    summary_f1 = ''.join(summary_f1)

    # Achievements, days active
    summary_f2 = f"Achievements: `{user.player.finishAchievementNum}` \n Spiral Abyss: `{user.player.towerFloorIndex}-{user.player.towerLevelIndex}` \n"

    p1_fields = [summary_f1, summary_f2]
    p1_fields.append()

    embeds = get_enka_user_summary_embeds(title=title, avatarId=avatarId, p1=p1_fields, nameCardId=nameCardId)
    return embeds

def get_enka_user_summary_embeds(nameCardId: int, avatarId : int, title: str, p1: list, p2=None, p3=None):
    embeds = []

    nameCard = getNameCard(nameCardId)
    profilePicture, icon = getProfilePicture(avatarId)

    e1 = create_embed(
        # Title: Player Summary
        # Name: Nickname / UID if error
        title=" ",
        name=" ",
        text=p1[0],
        icon=icon,
        color=VISION_TO_COLOR["Anemo"]
    )
    for i in range(1, len(p1)):
        e1.add_field(name=" ", value=p1[i], inline=False)
    
    e1.set_author(name=f"{title} Player Summary", icon_url=icon)
    e1.set_thumbnail(url=profilePicture)
    e1.set_image(url=nameCard)
    embeds.append(e1)
    return embeds