import datetime
import requests

from utils.constants import WEEKDAYS, CHAR_TO_URL
from utils.utils import create_embed, create_page_buttons

endpoint = "https://genshin.jmp.blue"

def get_characters():
    response = requests.get(endpoint + "/characters")
    characters = response.json()
    return characters

def get_character(name: str):
    url_name = CHAR_TO_URL[name] if name in CHAR_TO_URL else name.lower().replace(" ", "-")
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
    Get the passive talents of a Genshin Impact character.
    
    Parameters:
    name: str - Character name.

    Returns:
    list - list of dictionary of Character passive talents. 
        {
            "name": str, 
            "unlock": int, 
            "description": str,
            "level": int
        }
"""
def get_char_passive_talents_list(name: str):
    character = get_character(name)
    talents = character["passiveTalents"]
    return talents

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

def format_char_info(name: str, type: str):
    character = get_character(name)

    char_name = character["name"]
    skills = ["na", "e_skill", "e_burst", "passive", "constellations"]
    list = []
    result_str = ""
    if type not in skills:
        return f"Invalid skill type. Please choose from {skills}"
    else:
        if type == "na":
            list = get_char_combat_talents(name)
            result_str = f"**Normal Attack**\n{format_normal_attack(list)}"
        elif type == "e_skill":
            list = get_char_combat_talents(name)
            result_str = f"**Elemental Skill**\n{format_e_skill(list)}"
        elif type == "e_burst":
            list = get_char_combat_talents(name)
            result_str = f"**Elemental Burst**\n{format_e_burst(list)}"
        elif type == "passive":
            list = get_char_passive_talents_list(name)
            result_str = f"**Passive Talents**\n\n{format_passives_cons(list)}"
        elif type == "constellations":
            list = get_char_cons_list(name)
            result_str = f"**Constellations**\n\n{format_passives_cons(list)}"

    return f"**{char_name}** " + result_str
           # f"**Description:** {character['description']}\n"

def format_passives_cons(list: list):
    formatted_list = ""
    for item in list:
        formatted_list += f"**⦁ {item['name']}:** {item['description']}\n\n"
    return formatted_list

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
    return f"**{skill['name']}:**\n\n {skill['description']}\n\n"

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
        characters = books[book]
        characters_str = ""
        for character in characters:
            characters_str += f"⦁ {character.capitalize()}\n"
        embed = create_embed(
            name=book.capitalize(),
            title=f"Available Talent Books for {today}:",
            icon=get_guide_icon(book),
            text=characters_str,
            page=list(books.keys()).index(book) + 1,
            total_pages=len(books)
        )
        embeds.append(embed)
    return embeds

"""
    Get the character's icon.

    Parameters:
    name: str - Character name.

    Returns:
    url - Character icon url.
"""
def get_character_icon(name: str):
    url_name = CHAR_TO_URL[name] if name in CHAR_TO_URL else name.lower().replace(" ", "-")
    response = requests.get(endpoint + f"/characters/{url_name}/icon-big")
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