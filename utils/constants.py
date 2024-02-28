WEEKDAYS = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday'
}

"""
    Map of character names to a url-friendly version for genshin_dev.py
"""
CHAR_TO_URL = {
    "Raiden Shogun": "raiden",
    "Kujou Sara": "sara",
    "Sangonomiya Kokomi": "kokomi",
    "Kamisato Ayaka": "ayaka",
    "Kaedehara Kazuha": "kazuha",
    "Kamisato Ayato:": "ayato",
    "Childe": "tartaglia",

}

"""
    Map of character url-friendly name to their regular name.
"""
URL_TO_CHAR = {
    "raiden": "Raiden Shogun",
    "sara": "Kujou Sara",
    "kokomi": "Sangonomiya Kokomi",
    "ayaka": "Kamisato Ayaka",
    "kazuha": "Kaedehara Kazuha",
    "ayato": "Kamisato Ayato",
    
}

"""
    Map of character visions (hex) to their respective color.
"""
VISION_TO_COLOR = {

    "Pyro": 0xEF7938,
    "Hydro": 0x4cc2f1,
    "Anemo": 0x74c2a8,
    "Electro": 0xaf8ec1,
    "Cryo": 0x9fd6e3,
    "Geo": 0xfab632,
    "Dendro": 0xa5c83b,
}

"""
"""

"""
    Map of artifact stats to human-readable forms.
"""
PROP_TO_STAT = {
    "FIGHT_PROP_HP": "HP",
    "FIGHT_PROP_HP_PERCENT": "HP%",
    "FIGHT_PROP_ATTACK": "ATK",
    "FIGHT_PROP_ATTACK_PERCENT": "ATK%",
    "FIGHT_PROP_DEFENSE": "DEF",
    "FIGHT_PROP_DEFENSE_PERCENT": "DEF%",
    "FIGHT_PROP_ELEMENT_MASTERY": "Elemental Mastery",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "Energy Recharge",
    "FIGHT_PROP_CRITICAL": "Crit Rate",
    "FIGHT_PROP_CRITICAL_HURT": "Crit Damage",
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "Physical DMG Bonus",
    "FIGHT_PROP_ROCK_ADD_HURT": "Geo DMG Bonus",
    "FIGHT_PROP_WIND_ADD_HURT": "Anemo DMG Bonus",
    "FIGHT_PROP_ICE_ADD_HURT": "Cryo DMG Bonus",
    "FIGHT_PROP_WATER_ADD_HURT": "Hydro DMG Bonus",
    "FIGHT_PROP_FIRE_ADD_HURT": "Pyro DMG Bonus",
    "FIGHT_PROP_ELEC_ADD_HURT": "Electro DMG Bonus",
}


"""
    Map of Emoji Names to their respective ids.
"""
EMOJIS_TO_ID = {
    "adventurer_handbook": "<:adventurer_handbook:1212431650546393170>",
    "original_resin": "<:original_resin:1212431485034958878>",
    "realm_currency": "<:realm_currency:1212431054888112198>",
    "ore": "<:ore:1212464736382230670>",
    "daily_commission": "<:daily_commission:1212464737267490876>",
}
