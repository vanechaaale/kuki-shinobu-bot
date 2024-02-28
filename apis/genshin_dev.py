import datetime
import requests

from utils.constants import WEEKDAYS, CHAR_TO_URL, VISION_TO_COLOR
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
    embed - Embed of the character's combat talents, passive talents, or constellations.
"""
def embed_char_info(name: str, type: str):
    character = get_character(name)

    char_name = character["name"]
    skills = ["Normal Attack", "Elemental Skill", "Elemental Burst", "Passive Talents", "Constellations"]
    list = []
    result_str = ""
    embed_icon = ""
    show_more = False
    if type not in skills:
        return f"Invalid skill type. Please choose from {skills}"
    else:
        if type == "Normal Attack":
            list = get_char_combat_talents(name)
            result_str = format_normal_attack(list)
            embed_icon = get_talent_na_icon(name)
        elif type == "Elemental Skill":
            list = get_char_combat_talents(name)
            result_str = format_e_skill(list)
            embed_icon = get_talent_skill_icon(name)
        elif type == "Elemental Burst":
            list = get_char_combat_talents(name)
            result_str = format_e_burst(list)
            embed_icon = get_talent_burst_icon(name)
        elif type == "Passive Talents":
            return create_passive_talent_embed(name)
        elif type == "Constellations":
            return create_constellations_embed(name)

    details, more = result_str.split('.')[0], result_str.split('.')[1:]

    embed = create_embed(
        name=" ",
        title=f"{char_name}: {type}",
        icon=embed_icon,
        text=f'{result_str}' if show_more else f'{details}.',
        color=VISION_TO_COLOR[get_vision(name)],
        page=1,
        total_pages=1
    )
    embed.set_thumbnail(url=embed_icon)
    return embed
        # f"**{char_name}** " + result_str
        # f"**Description:** {character['description']}\n"

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
        title=f"{char_name}: Passive Talents",
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
    return embed

def create_constellations_embed(name: str):
    character = get_character(name)
    char_name = character["name"]
    list = get_char_cons_list(name)
    cons_list = format_constellations(list)
    embed_icon = get_character_icon(name)
    embed_image = get_character_constellation(name)

    embed = create_embed(
        name=" ",
        title=f"{char_name}: Constellations",
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
    return embed

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
        if skill['unlock'] == "Normal Attack":
            return format_combat_talent_str(skill)
        
def format_e_skill(list: list):
    for skill in list:
        if skill['unlock'] == "Elemental Skill":
            return format_combat_talent_str(skill)

def format_e_burst(list: list):
    for skill in list:
        if skill['unlock'] == "Elemental Burst":
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
    today = WEEKDAYS[datetime.datetime.now().weekday()]
    embeds = []
    for book in books:
        icon = get_guide_icon(book)
        characters = books[book]
        characters_str = []
        for character in characters:
            characters_str.append(f"⦁ {character.capitalize()}\n")
        characters_str = ''.join(characters_str)
        embed = create_embed(
            name=book.capitalize(),
            title=f"Available Talent Books for {today}:",
            icon=icon,
            text=characters_str,
            page=list(books.keys()).index(book) + 1,
            total_pages=len(books)
        )
        embed.set_thumbnail(url=icon)
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
        return ""
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

