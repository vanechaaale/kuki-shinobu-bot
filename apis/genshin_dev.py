import datetime
import requests

from utils.constants import WEEKDAYS, CHAR_TO_URL, VISION_TO_COLOR, CharacterSkills
from utils.utils import create_embed

endpoint = "https://genshin.jmp.blue"

def get_characters():
    response = requests.get(endpoint + "/characters")
    characters = response.json()
    return characters

def get_character(name: str):
    # check if character name is in CHAR_TO_URL, not case sensitive
    url_name = get_char_url_name(name)
    characters = get_characters()
    for character in characters:
        if character.lower() == url_name.lower():
            response = requests.get(endpoint + f"/characters/{url_name}")
            char = response.json()
            return char
    raise Exception(f"Character {name} not found.")

"""
    Get the normal attack, skill, and burst talents of a Genshin Impact character.

    Parameters:
    name: str - Character name.

    Returns:
    list - list of dictionary of Character combat talents. 
        {
            "name": str, 
            "unlock": int, 
            "description": str, 
            "upgrades": list of dict("name": str, "value": str)
        }
"""
def get_char_combat_talents(name: str):
    character = get_character(name)
    skillTalents = character["skillTalents"]
    return skillTalents

"""
    Get the constellations of a Genshin Impact character.

    Parameters:
    name: str - Character name.

    Returns:
    list - list of dictionary of Character constellations. 
        {
            "name": str, 
            "unlock": int, 
            "description": str,
            "level": int
        }
"""
def get_char_cons_list(name: str):
    character = get_character(name)
    cons = character["constellations"]
    return cons

"""
    Get the character's  combat talents, passive talents, or constellations info.

    Parameters:
    name: str - Character name.
    type: str - Type of skill. (Normal Attack, Elemental Skill, Elemental Burst, Passive, Constellations)

    Returns:
    tuple - (list of Embeds, bool)
        list of Embeds - list of embeds for the character's combat talents, passive talents, or constellations.
        bool - True if the talent has scalings, False if not.
"""
def embed_char_skill_info(name: str, type: str):
    character = get_character(name)

    char_name = character["name"]
    skills = [skill.value for skill in CharacterSkills]
    talents = []
    scalings = False
    result_str = ""
    embed_icon = ""
    upgrades_str = ""
    if type not in skills:
        return f"Invalid skill type. Please choose from {skills}"
    else:
        if type == CharacterSkills.NORMAL_ATTACK.value:
            talents = character["skillTalents"]
            result_str = format_normal_attack(talents)
            embed_icon = get_talent_na_icon(name)
            upgrades_str, scalings = get_talent_upgrades(character, type)
        elif type == CharacterSkills.ELEMENTAL_SKILL.value:
            talents = character["skillTalents"]
            result_str = format_e_skill(talents)
            embed_icon = get_talent_skill_icon(name)
            upgrades_str, scalings = get_talent_upgrades(character, type)
        elif type == CharacterSkills.ELEMENTAL_BURST.value:
            talents = character["skillTalents"]
            result_str = format_e_burst(talents)
            embed_icon = get_talent_burst_icon(name)
            upgrades_str, scalings = get_talent_upgrades(character, type)
        elif type == CharacterSkills.PASSIVE_TALENTS.value:
            return create_passive_talent_embed(name)
        elif type == CharacterSkills.CONSTELLATIONS.value:
            return create_constellations_embed(name)

    # If it's too long, redirect link to wiki
    if len(result_str) > 800:
        skill_name = talents[0]['name']
        result_str = f"{result_str[:770]}... [Read More](https://genshin-impact.fandom.com/wiki/{skill_name.replace(' ', '_')})\n\n"

    embeds = []

    summary_embed = create_embed(
        name=" ",
        title=f"{char_name}: {type}",
        icon=embed_icon,
        text=result_str,
        color=VISION_TO_COLOR[get_vision(name)],
        page=1,
        total_pages=2 if scalings else 1
    )
    summary_embed.set_thumbnail(url=embed_icon)
    embeds.append(summary_embed)

    if scalings:
        scalings_embed = create_embed(
            name="Ability Details",
            title=f"{char_name}: {type}",
            icon=embed_icon,
            text=upgrades_str,
            color=VISION_TO_COLOR[get_vision(name)],
            page=2,
            total_pages=2
        )
        scalings_embed.set_thumbnail(url=embed_icon)
        embeds.append(scalings_embed)
    return (embeds, scalings)

def create_combat_talent_embed(name: str):
    pass

def create_passive_talent_embed(name: str):
    character = get_character(name)
    char_name = character["name"]
    list = character["passiveTalents"]
    passive_talents_list = format_passive_talents(list)
    embed_icon = get_character_icon(name)

    embed = create_embed(
        name=" ",
        title=f"{char_name}: {CharacterSkills.PASSIVE_TALENTS.value}",
        # icon=embed_icon,
        text=passive_talents_list[0],
        color=VISION_TO_COLOR[get_vision(name)],
        page=1,
        total_pages=1
    )
    for i, talent in enumerate(passive_talents_list):
        if i == 0:
            continue
        embed.add_field(
            name=" ",
            value=talent,
            inline=False
        )
    embed.set_thumbnail(url=embed_icon)
    return ([embed], False)

def create_constellations_embed(name: str):
    character = get_character(name)
    char_name = character["name"]
    list = get_char_cons_list(name)
    cons_list = format_constellations(list)
    embed_icon = get_character_icon(name)
    embed_image = get_character_constellation(name)

    embed = create_embed(
        name=" ",
        title=f"{char_name}: {CharacterSkills.CONSTELLATIONS.value}",
        # icon=embed_icon,
        text=cons_list[0],
        color=VISION_TO_COLOR[get_vision(name)],
        page=1,
        total_pages=1
    )
    for i, con in enumerate(cons_list):
        if i == 0:
            continue
        embed.add_field(
            name=" ",
            value=con,
            inline=False
        )
    embed.set_thumbnail(url=embed_image)
    return ([embed], False)

def format_passive_talents(list: list):
    formatted_list = []
    for item in list:
        desc = format_passive_talent_str(item)
        if len(desc) > 300:
            formatted_list.append(f"{desc[:250]}... [Read More](https://genshin-impact.fandom.com/wiki/{item['name'].replace(' ', '_')})\n\n")
        else:
            formatted_list.append(desc)
    return formatted_list

def format_constellations(list: list):
    cons_list = []
    for i, item in enumerate(list):
        formatted_con = format_constellation_str(i, item)
        cons_list.append(formatted_con)
    return cons_list

def format_normal_attack(list: list):
    for skill in list:
        if skill['unlock'] == CharacterSkills.NORMAL_ATTACK.value:
            return format_combat_talent_str(skill)
        
def format_e_skill(list: list):
    for skill in list:
        if skill['unlock'] == CharacterSkills.ELEMENTAL_SKILL.value:
            return format_combat_talent_str(skill)

def format_e_burst(list: list):
    for skill in list:
        if skill['unlock'] == CharacterSkills.ELEMENTAL_BURST.value:
            return format_combat_talent_str(skill)
        
def format_combat_talent_str(skill: dict):
    return f"**{skill['name']}**\n\n {skill['description']}\n\n"

def format_constellation_str(i: int, item: dict):
    con_desc =  f"**C{i + 1}: {item['name']}\n** {item['description']}\n\n"
    if (len(con_desc) > 250):
        return f"{con_desc[:220]}... [Read More](https://genshin-impact.fandom.com/wiki/{item['name'].replace(' ', '_')})\n\n"
    return con_desc

def format_passive_talent_str(item: dict):
    return f"**- {item['name']}:\n** {item['description']}\n\n"

def format_talent_upgrades_list(list: list):
    upgrades = []
    for upgrade in list:
        upgrades.append(f"- {upgrade['name']}: {upgrade['value']}\n")
    return ''.join(upgrades)

def get_talent(character: dict, type: str):
    for talent in character["skillTalents"]:
        if talent['unlock'] == type:
            return talent
        
def get_talent_upgrades(character: dict, type: str):
    upgrades_str = ""
    scalings = False
    talent = get_talent(character, type)
    if 'upgrades' in talent:
        upgrades_list = talent['upgrades']
        scalings = True
        upgrades_str = format_talent_upgrades_list(upgrades_list)
    return (upgrades_str, scalings)
                

"""
    Get the available talent books for the day and the characters that use the books.

    Returns:
    dict("book": str, dict("availability": list, "characters": list))
"""
def get_daily_talent_books():
    all_talent_books = get_talent_books()
    daily_books = {}
    # Today's date (PST)
    today = WEEKDAYS[datetime.datetime.now().weekday()]
    for book in all_talent_books:
        if today in all_talent_books[book]['availability']:
            daily_books[book] = all_talent_books[book]['characters']
    return daily_books

"""
    Get all the talent books and the characters that use the books.

    Returns:
    dict("book": str, dict("availability": list, "characters": list))
"""
def get_talent_books():
    response = requests.get(endpoint + "/materials/talent-book")
    result = {}
    books = response.json()
    for book in books:
        result[book] = {
            'availability': books[book]['availability'],
            'characters': books[book]['characters']
            }
    return result

"""
    Return a list of embeds for the available talent books for the day.

    Returns:
    list of Embeds
"""
def get_daily_talent_books_embeds():
    books = get_daily_talent_books()
    embeds = []
    for book in books:
        icon = get_guide_icon(book)
        characters = books[book]
        # 4 chars per column
        rows = []
        col = []
        for i, char in enumerate(characters):
            if i % 4 == 0 and i != 0:
                col = ', '.join(col)
                rows.append(col)
                col = []
            col.append(char.capitalize())
        col = ', '.join(col)
        rows.append(col)
        rows = '\n'.join(rows)
        embed = create_embed(
            title=f"{book.capitalize()}",
            name="Used By:",
            text=f"{rows}",
            page=list(books.keys()).index(book) + 1,
            total_pages=len(books)
        )

        embed.set_image(url=icon)
        embeds.append(embed)

    return embeds

"""
    Get the character's icon.

    Parameters:
    name: str - Character name.

    Returns:
    url - Character icon url1.
"""
def get_character_icon(name: str):
    url_name = CHAR_TO_URL[name] if name in CHAR_TO_URL else name.lower().replace(" ", "-")
    response = requests.get(endpoint + f"/characters/{url_name}/icon-big")
    icon = response.url
    return icon

"""
    Get the character's constellation icon.

    Parameters:
    name: str - Character name.

    Returns:
    url - Character constellation icon url.
"""
def get_character_constellation(name: str):
    url_name = CHAR_TO_URL[name] if name in CHAR_TO_URL else name.lower().replace(" ", "-")
    response = requests.get(endpoint + f"/characters/{url_name}/constellation")
    if response.status_code != 200:
        return get_character_icon(name)
    icon = response.url
    return icon

"""
    Get a character's vision.

    Parameters:
    name: str - Character name.

    Returns:
    str - Character vision.
"""
def get_vision(name: str):
    character = get_character(name)
    return character['vision']

"""
    Get the talent book icon.

    Parameters:
    name: str - Talent book name.

    Returns:
    url - Talent book icon url.
"""
def get_guide_icon(name: str):
    # https://genshin.jmp.blue/materials/talent-book/guide-to-admonition
    url = endpoint + f"/materials/talent-book/guide-to-{name.lower()}"
    response = requests.get(url)
    icon = response.url
    return icon

def get_talent_na_icon(name: str):
    # https://genshin.jmp.blue/characters/ganyu/talent-na
    url_name = get_char_url_name(name)
    url = endpoint + f"/characters/{url_name}/talent-na"
    response = requests.get(url)
    if response.status_code != 200:
        return get_character_icon(name)
    icon = response.url
    return icon

def get_talent_skill_icon(name: str):
    # https://genshin.jmp.blue/characters/ganyu/talent-skill
    url_name = get_char_url_name(name)
    url = endpoint + f"/characters/{url_name}/talent-skill"
    response = requests.get(url)
    if response.status_code != 200:
        return get_character_icon(name)
    icon = response.url
    return icon

def get_talent_burst_icon(name: str):
    # https://genshin.jmp.blue/characters/ganyu/talent-burst
    url_name = get_char_url_name(name)
    url = endpoint + f"/characters/{url_name}/talent-burst"
    response = requests.get(url)
    if response.status_code != 200:
        return get_character_icon(name)
    icon = response.url
    return icon

def get_char_url_name(name: str):
    for key in CHAR_TO_URL:
        if name.lower() == key.lower():
            name = key
    url_name = CHAR_TO_URL[name] if name in CHAR_TO_URL.keys() else name.lower().replace(" ", "-")
    return url_name

"""
    Get the artifact icon for a flower of life for the artifact set.

    Parameters:
    icon_name: str - Artifact set name.

    Returns:
    url - Artifact icon url.
"""
def get_artifact_icon(icon_name: str):
    # to lowercase and replace all apostrophes with hyphens
    url_name = icon_name.lower().replace("'", "-")
    url = endpoint + f"/artifact/{url_name}/flower-of-life"
    response = requests.get(url)
    icon = response.url
    return icon

