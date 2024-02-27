import genshin
import requests
from utils.constants import VISION_TO_COLOR

from utils.mongo_db import *
from utils.utils import create_embed

async def main():
    data = await client.get_genshin_user(601328008)
    print(f"User has a total of {data.stats.characters} characters")

def wish_history():
    print(client.wish_history())

async def redeem(code: str):
    print(await client.redeem_code(code))

async def get_abyss_data():
    print(await client.get_spiral_abyss())

async def get_owned_characters():
    print(await client.get_calculator_characters(sync=True))

"""
    Get the Genshin API client for a Discord user.

    Parameters:
    discord_id: Discord user id.

    Returns: 
    genshin.Client - Genshin API client.
"""
async def get_genshin_api_client(discord_id: int):
    user = get_user_from_db(discord_id)
    cookies = user['authentication_tokens']
    client = genshin.Client(cookies, game=genshin.Game.GENSHIN)
    return client

"""
    Authenticate the HoyoLab cookies and Genshin Account UID for a Discord user.

    Parameters:
    discord_id: Discord user id.
    uid: Optional Genshin player UID.
    ltuid: ltuid_v2.
    ltmid: ltmid_v2.
    ltoken: ltoken_v2.

    Returns: 
    str - Success message.
"""
async def authenticate(discord_id: int, uid: int, ltuid: int, ltmid: str, ltoken: str, cookie_token: str):
    cookies = {
        "ltuid_v2": ltuid, 
        "ltmid_v2": ltmid, 
        "ltoken_v2": ltoken,
        "cookie_token_v2": cookie_token,
        "account_id_v2": ltuid,
        "account_mid_v2": ltmid,
        }
    client = genshin.Client(cookies, game=genshin.Game.GENSHIN)
    initial_user = get_user_from_db(discord_id) if get_user_from_db(discord_id) else None
    try:
        # add cookies to payload
        payload = {
            "discord_id": str(discord_id),
            "authentication_tokens": cookies,
        }
        if uid:
            payload["uid"] = uid

        # 1) Check if discord user's genshin info is already in database
        if not get_user_from_db(discord_id):
            # 2) If not, add user to database
            add_to_users(payload)
        else:
            # 3) Else update user data
            update_user(discord_id, payload)

        # Check if cookies are invalid by trying to query a user
        await client.get_genshin_user(uid)

    except genshin.errors.InvalidCookies:
        # Revert to previous user data if cookies are invalid
        if initial_user:
            update_user(discord_id, initial_user)
        return "Error during HoyoLab authentication. Please check your credentials and try again."
    return "Successfully authenticated HoyoLab cookies/Genshin Account info."

"""
    Get the Genshin player's summary. If no UID is provided, default to author's UID. 

    Parameters:
    uid: int - Genshin player UID.
    discord_id: int - Discord user id.

    Returns:
    str - Genshin player summary string.
"""
async def get_genshin_api_user_summary(discord_id: int, uid: int = False):
    if not uid:
        # Get author's UID
        author = get_user_from_db(discord_id)
        uid = author['uid']
    client = await get_genshin_api_client(discord_id)
    user = await client.get_genshin_user(uid)
    summary_str = f"Nickname: {user.info.nickname}\n"
    summary_str += f"UID: {uid}\n"
    summary_str += f"Days Active: {user.stats.days_active}\n"
    summary_str += f"Achievements: {user.stats.achievements}\n"
    summary_str += f"Spiral Abyss: {user.stats.spiral_abyss}\n"
    summary_str += f"Characters Owned: {user.stats.characters}\n"

    return summary_str

"""
    Get a Genshin player's resin, comissions, realm currency, and expeditions info.

    Errors:
    [10102] Cannot view real-time notes of other users.
        - If the uid from the database doesn't match the hoyolab uid/cookies, this error will be raised.

    Parameters:
    discord_id: int - Discord user id.

    Returns:
    embed - Genshin player notes embed.

"""
async def get_notes_embed(discord_id: int):
    client = await get_genshin_api_client(discord_id)
    user = get_user_from_db(discord_id)
    uid = user['uid']
    
    notes = await client.get_notes(int(uid))

    # datetime.timedelta object
    time = notes.remaining_resin_recovery_time
    # Convert seconds to hours and minutes
    hours = time.total_seconds() // 3600
    minutes = (time.total_seconds() % 3600) // 60

    # datetime.timedelta object
    time = notes.remaining_realm_currency_recovery_time
    # Convert to days and hours
    days = time.days
    hours = time.seconds // 3600

    notes_str = ""
    notes_str += f"Current resin: {notes.current_resin}/{notes.max_resin}\n"
    notes_str += f"Resin full in {hours:.0f} hours {minutes:.0f} minutes\n"
    notes_str += f"Commissions left: {notes.completed_commissions}/{notes.max_commissions}\n"
    notes_str += f"Current realm currency: {notes.current_realm_currency}/{notes.max_realm_currency}\n"
    notes_str += f"Realm currency full in {days} days {hours} hours\n"
    notes_str += f"Expeditions finished: {sum(expedition.finished for expedition in notes.expeditions)}\n"

    icon_img = "https://static.wikia.nocookie.net/gensin-impact/images/3/35/Item_Fragile_Resin.png/revision/latest?cb=20210106074218"
    request = requests.get(icon_img)
    icon = request.url

    embed = create_embed(
        title="Real-time Notes:",
        name=" ",
        text=notes_str,
        icon=icon,
        color=VISION_TO_COLOR["Anemo"],
    )
    embed.set_thumbnail(url=icon)

    return embed


async def claim_daily_rewards(discord_id: int):
    client = await get_genshin_api_client(discord_id)
    message = await client.claim_daily_reward()
    return str(message)

async def redeem_code(code: str, discord_id: int):
    client = await get_genshin_api_client(discord_id)
    message = await client.redeem_code(code)
    return message

