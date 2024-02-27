import requests
endpoint = "https://genshin.jmp.blue"

def get_characters():
    response = requests.get(endpoint + "/characters")
    characters = response.json()
    return characters

def get_character(name: str):
    response = requests.get(endpoint + f"/characters/{name}")
    character = response.json()
    return character

def get_character_talents(name: str):
    character = get_character(name)
    talents = character["talents"]
    return talents