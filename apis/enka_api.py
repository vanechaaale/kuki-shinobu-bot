import requests
import chompjs

from enkapy import Enka
from apis.genshin_dev import get_artifact_icon, get_character_icon, get_vision
from utils.mongo_db import get_user_from_db
from utils.utils import *
from utils.constants import VISION_TO_COLOR, PROP_TO_STAT

client = Enka()

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

"""
    Get a Genshin Account's Profile Picture

    Parameters:
        avatarId: int - Genshin player AvatarIcon id

    Returns:
        str - Genshin player profile picture url or empty string if no avatar was found
"""
def getProfilePicture(avatarId: int):
    # enka network url for avatar ids to avatar icons in a js object
    avatar_url = "https://enka.network/_app/immutable/chunks/pfps.94a09dfc.js"
    req = requests.get(avatar_url)
    if (req.status_code == 200):
        js = req.content.decode('utf-8')
        js_objs = js.replace('const n=', '').replace(';export{t as G,n as H};\n', '')
        # only want the second object t, I don't think I care about the first one n
        # find index of the second object
        avatar_dict_idx = js_objs.find(',t=') + 3
        avatar_dict_js = js_objs[avatar_dict_idx:]
        # parse the js object into a python dictionary
        avatar_icon_dict = chompjs.parse_js_object(avatar_dict_js)
        # get the avatar icon url from the dictionary
        iconPath = avatar_icon_dict[str(avatarId)]['iconPath']
        avatar_icon_url = f"https://enka.network/ui/{iconPath}.png"
        icon_req = requests.get(avatar_icon_url)
        if (icon_req.status_code == 200):
            return icon_req.url, avatar_icon_url
    return ""

"""
    Get a Genshin Account's Name Card

    Parameters:
        nameCardId: int - Genshin player NameCard id

    Returns:
        str - Genshin player name card url or empty string if no name card was found
"""
def getNameCard(nameCardId: int):
     # Namecard
    res_url = f"https://api.ambr.top/v2/EN/namecard/{nameCardId}?vh=44F5"
    res = requests.get(res_url).json()
    if res["response"] == 200:
        data = res["data"]
        iconName = data['icon'].replace("Icon", "Pic")
        url = f"https://api.ambr.top/assets/UI/namecard/{iconName}_P.png?vh=2024020300"
        namecard_response = requests.get(url)
        if namecard_response.status_code == 200:
            return namecard_response.url
    return ""

async def get_user_showcase(uid: int, discord_id: int):
    # If UID is not provided, look for the author's UID
    await client.load_lang()
    if not uid:
        user = get_user_from_db(discord_id)
        uid = user['uid']

    user = await client.fetch_user(uid)
    # showcase_str = f"UID: {uid}\n"

    showcased_chars_combat = []
    for character in user.characters:
        showcased_char_combat = get_char_combat_data(character)

        showcased_char_artifacts, set_bonus = get_char_artifact_data(character)

        showcase_dict = {
            "name": character.name,
            "vision": get_vision(character.name),
            "description": showcased_char_combat,
            "artifacts": showcased_char_artifacts,
            "set_bonus": set_bonus
        }
        showcased_chars_combat.append(showcase_dict)

    showcased_embeds = []
    for character in showcased_chars_combat:
        page_index = showcased_chars_combat.index(character) + 1
        icon = get_character_icon(character["name"])
        vision_color = VISION_TO_COLOR[character["vision"]]
        embed = create_embed(
            title=character["name"],
            name=" ", 
            text=character["description"], 
            icon=icon, 
            color=vision_color,
            page=page_index,
            total_pages=len(showcased_chars_combat)
            )
        embed.add_field(
            name=f"{character['set_bonus']}\n",
            value='\n\n'.join(character["artifacts"]),
            inline=False
        )
        embed.set_thumbnail(url=icon)
        showcased_embeds.append(embed)

    return showcased_embeds

def get_char_combat_data(character):
    showcased_char_combat = []
    showcased_char_combat.append(f'C{str(len(character.internal_constellations))} ')
    showcased_char_combat.append(f"Lv. {character.level}\n\n")
    weapon = character.weapon
    showcased_char_combat.append(f'Weapon: R{weapon.refine} {weapon.name} Lv.{weapon.level} \n\n')

    showcased_char_combat.append('Combat Talents:\n')

    skill_details = {}
    for skill in character.skills:
        if skill.type == 0:
            skill_details['na'] = skill.level
        elif skill.type == 1:
            skill_details['skill'] = skill.level
        elif skill.type == 2:
            skill_details['burst'] = skill.level

    showcased_char_combat.append(f'⦁\tNormal Attack: {skill_details["na"]}\n')
    showcased_char_combat.append(f'⦁\tElemental skill: {skill_details["skill"]}\n')
    showcased_char_combat.append(f'⦁\tElemental burst: {skill_details["burst"]}\n')

    return ''.join(showcased_char_combat)

def get_char_artifact_data(character):
    showcased_char_artifacts = []
    set_bonus = ""
    occurrence_dict = {}
    for artifact in character.artifacts:
        showcased_char_artifact = []
        artifact_icon = get_artifact_icon(artifact.set_name)
        
        showcased_char_artifact.append(f'**{artifact.name}**:\n ')
        showcased_char_artifact.append(f'**{artifact.main_stat.value} {PROP_TO_STAT[artifact.main_stat.prop]}**\n')
        for sub_stats in artifact.sub_stats:
            showcased_char_artifact.append(f'{PROP_TO_STAT[sub_stats.prop]}: {sub_stats.value}, ')
        showcased_char_artifact = ''.join(showcased_char_artifact)
        
        showcased_char_artifacts.append(showcased_char_artifact)

        if artifact.set_name in occurrence_dict:
            occurrence_dict[artifact.set_name] += 1
        else:
            occurrence_dict[artifact.set_name] = 1
    
    for set_name, occurrence in occurrence_dict.items():
        if 1 < occurrence < 4 :
            set_bonus += f"2 pc {set_name}\n" if len(set_bonus) > 0 else f"2 pc {set_name}/"
        elif occurrence == 4:
            set_bonus = f'4 pc {set_name}\n'
    return showcased_char_artifacts, set_bonus