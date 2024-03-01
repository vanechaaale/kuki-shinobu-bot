import requests
import json

from enkapy import Enka
from apis.genshin_dev import get_artifact_icon, get_character_icon, get_vision
from utils.mongo_db import get_user_from_db
from utils.utils import *
from utils.constants import VISION_TO_COLOR, PROP_TO_STAT
from splinter import Browser
 

client = Enka()


# Testing the Enka API
async def main():
    await client.load_lang()
    user = await client.fetch_user(601328008)
    # case for unknown characters in username
    try: 
        print(f"Nickname: {user.player.nickname}")
    except UnicodeEncodeError:
        print("couldn't print nickname :(")
        
    print(f"Level: {user.player.level}")
    print(f'Signature: {user.player.signature}')
    print(f'World level:{user.player.worldLevel}')
    print(f'Abyss: {user.player.towerFloorIndex}-{user.player.towerLevelIndex}')
    # fetch first character
    if user.characters:
        character = user.characters[0]
        print(f'Name: {character.name}')
        print(f'Ascension: {character.ascension}')
        print(f'Level: {character.level}')
        print(f'Exp: {character.experience}')
        print('Weapon:')
        weapon = character.weapon
        print(f'\tName: {weapon.name}')
        print(f'\tLevel: {weapon.level}')
        print(f'\tRefine: {weapon.refine}')
        print(f'\tStar level: {weapon.rank}')
    
        print('Constellations:')
        for constellation in character.constellations:
            if constellation.activated:
                print(f'\t{constellation.name} Activated')
        print('Skills:')
        for skill in character.skills:
            if skill.type == 0:
                print(f'\tNormal Attack level: {skill.level}')
            elif skill.type == 1:
                print(f'\tElemental skill level: {skill.level}')
            elif skill.type == 2:
                print(f'\tElemental burst level: {skill.level}')
        print('Artifacts:')
        for artifact in character.artifacts:
            print(f'\t{artifact.set_name} {artifact.name}:')
            print(f'\t{artifact.main_stat.prop}:{artifact.main_stat.value}')
            for sub_stats in artifact.sub_stats:
                print(f'\t\t{sub_stats.prop}:{sub_stats.value}')

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
    summary_str = []

    # case for unknown characters in username (looking at you, Greg)
    try: 
        title = user.player.nickname
        summary_str.append(f"UID: {uid}")
    except UnicodeEncodeError:
        title = str(uid)

        
    summary_str.append(f"Level: {user.player.level}\n")
    summary_str.append(f'Signature: {user.player.signature}\n')
    summary_str.append(f'Abyss: {user.player.towerFloorIndex}-{user.player.towerLevelIndex}\n')
    summary_str.append(f'Characters owned: {len(user.characters)}')
    summary_str = ''.join(summary_str)

    embeds = get_enka_user_summary_embeds(title=title, p1=summary_str, nameCardId=nameCardId)
    return embeds

def get_enka_user_summary_embeds(nameCardId: int, title: str, p1: str, p2=None, p3=None):
    embeds = []
    namecard = ""
    e1 = create_embed(
        title=title,
        name=" ",
        text=p1,
        color=VISION_TO_COLOR["Anemo"]
    )
    res_url = f"https://api.ambr.top/v2/EN/namecard/{nameCardId}?vh=44F5"
    res = requests.get(res_url).json()
    if res["response"] == 200:
        data = res["data"]
        iconName = data['icon'].replace("Icon", "Pic")
        print("iconName: ", str(iconName))
        url = f"https://api.ambr.top/assets/UI/namecard/{iconName}_P.png?vh=2024020300"
        namecard_response = requests.get(url)
        if namecard_response.status_code == 200:
            namecard = namecard_response.url
    e1.set_image(url=namecard)
    embeds.append(e1)
    return embeds

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