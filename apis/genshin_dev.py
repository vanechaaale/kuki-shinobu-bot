import requests
endpoint = "https://genshin.jmp.blue"

def get_characters():
    response = requests.get(endpoint + "/characters")
    characters = response.json()
    return characters

def get_character(name: str):
    characters = get_characters()
    for character in characters:
        if character.lower() == name.lower():
            response = requests.get(endpoint + f"/characters/{name}")
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