from enkapy import Enka
from mongo_db import get_user_from_db

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
async def get_user_summary(uid: int, discord_id: int):
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
    showcase_str = f"UID: {uid}\n"
    for character in user.characters:
        showcase_str += f"Name: {character.name}\n"
        showcase_str += f"Level: {character.level}\n"
        # showcase_str += 'Weapon:\n'
        # weapon = character.weapon
        # showcase_str += f'\tName: {weapon.name}\n'
        # showcase_str += f'\tLevel: {weapon.level}\n'
        # showcase_str += f'\tRefine: {weapon.refine}\n'
        # showcase_str += f'\tStar level: {weapon.rank}\n'
    
        showcase_str += 'Constellation: ' + str(len(character.internal_constellations)) + '\n'
        showcase_str += 'Combat Talents:'
        for skill in character.skills:
            if skill.type == 0:
                showcase_str += f'{skill.level}\ '
            elif skill.type == 1:
                showcase_str += f'{skill.level}\ '
            elif skill.type == 2:
                showcase_str += f'{skill.level}\n'
        # showcase_str += 'Artifacts:\n'
        # for artifact in character.artifacts:
        #     showcase_str += f'\t{artifact.set_name} {artifact.name}:\n'
        #     showcase_str += f'\t{artifact.main_stat.prop}:{artifact.main_stat.value}\n'
        #     for sub_stats in artifact.sub_stats:
        #         showcase_str += f'\t\t{sub_stats.prop}:{sub_stats.value}\n'
    return showcase_str
