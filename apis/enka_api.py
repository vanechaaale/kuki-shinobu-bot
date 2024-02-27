from enkapy import Enka
from apis.genshin_dev import get_character_icon, get_vision
from utils.mongo_db import get_user_from_db
from utils.utils import *
from utils.constants import VISION_TO_COLOR

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

    Requirements: Cookies & Authentication

    Parameters:
        uid: int - Genshin player UID

    Returns:
        str - Genshin player summary string containing, UID, Nickname, Level, Signature, and Abyss floor
"""
async def get_enka_user_summary(uid: int, discord_id: int):
    # If UID is not provided, look for the author's UID
    await client.load_lang()
    if not uid:
        user = get_user_from_db(discord_id)
        uid = user['uid']

    user = await client.fetch_user(uid)
    summary_str = f"UID: {uid}\n"

    # case for unknown characters in username (looking at you, Greg)
    try: 
        summary_str += f"Nickname: {user.player.nickname}\n"
    except UnicodeEncodeError:
        print("couldn't print nickname :(")
        
    summary_str += f"Level: {user.player.level}\n"
    summary_str += f'Signature: {user.player.signature}\n'
    summary_str += f'Abyss: {user.player.towerFloorIndex}-{user.player.towerLevelIndex}\n'
    return summary_str

async def get_user_showcase(uid: int, discord_id: int):
    # If UID is not provided, look for the author's UID
    await client.load_lang()
    if not uid:
        user = get_user_from_db(discord_id)
        uid = user['uid']

    user = await client.fetch_user(uid)
    # showcase_str = f"UID: {uid}\n"

    showcased_chars = []
    for character in user.characters:
        showcased_char = ""
        showcased_char += f"Level: {character.level}\n"
        weapon = character.weapon
        showcased_char += f'Weapon:{weapon.name} R{weapon.refine} Lv.{weapon.level}\n'
    
        showcased_char += 'Constellation: ' + str(len(character.internal_constellations)) + '\n'
        showcased_char += 'Combat Talents:\n'

        skill_details = {}
        for skill in character.skills:
            if skill.type == 0:
                skill_details['na'] = skill.level
            elif skill.type == 1:
                skill_details['skill'] = skill.level
            elif skill.type == 2:
                skill_details['burst'] = skill.level

        showcased_char += f'⦁\tNormal Attack: {skill_details["na"]}\n'
        showcased_char += f'⦁\tElemental skill: {skill_details["skill"]}\n'
        showcased_char += f'⦁\tElemental burst: {skill_details["burst"]}\n'

        # showcase_str += 'Artifacts:\n'
        # for artifact in character.artifacts:
        #     showcase_str += f'\t{artifact.set_name} {artifact.name}:\n'
        #     showcase_str += f'\t{artifact.main_stat.prop}:{artifact.main_stat.value}\n'
        #     for sub_stats in artifact.sub_stats:
        #         showcase_str += f'\t\t{sub_stats.prop}:{sub_stats.value}\n'
        

        showcase_dict = {
            "name": character.name,
            "vision": get_vision(character.name),
            "description": showcased_char
        }
        showcased_chars.append(showcase_dict)

    showcased_embeds = []
    for character in showcased_chars:
        page_index = showcased_chars.index(character) + 1
        icon = get_character_icon(character["name"])
        vision_color = VISION_TO_COLOR[character["vision"]]
        embed = create_embed(
            name=character["name"], 
            text=character["description"], 
            icon=icon, 
            color=vision_color,
            page=page_index,
            total_pages=len(showcased_chars)
            )
        showcased_embeds.append(embed)

    return showcased_embeds