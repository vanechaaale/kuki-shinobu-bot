import asyncio
import json
import genshin

from mongo_db import *

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
async def authenticate(discord_id: int, uid: int, ltuid: int, ltmid: str, ltoken: str):
    cookies = {"ltuid": ltuid, 
            "ltmid_v2": ltmid, 
            "ltoken_v2": ltoken}
    client = genshin.Client(cookies, game=genshin.Game.GENSHIN)
    try:
        # add cookies to payload
        payload = {
            "discord_id": str(discord_id),
            "authentication_tokens": cookies,
        }
        if uid:
            payload["uid"] = uid
        # 1) Check if discord user is already in database
        # 2) If not, add user to database
        # 3) Else update user data
        if not get_user_from_db(discord_id):
            add_to_users(discord_id, uid, ltuid, ltmid, ltoken)
        else:
            update_user(discord_id, payload)
        # try fetching user data with cookies
        await client.get_genshin_user(uid)
    except genshin.errors.InvalidCookies:
        return "Invalid cookies"
    return "Successfully authenticated HoyoLab cookies/Genshin Account info."

async def claim_daily_rewards(discord_id: int):
    client = await get_genshin_api_client(discord_id)
    message = await client.claim_daily_reward()
    return message 
        

# asyncio.run(main())