import datetime
import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)

"""
    Add a discord user to the database.

    Parameters:
      payload: dict - Discord user information.
   
    Returns:
      The user added to the database.
"""
def add_to_users(payload: dict):
   discord_id = payload['discord_id']
   uid = payload['uid']
   authentication_tokens = payload['authentication_tokens']

   # Get reference to Discord Users database
   db = client['discord_users']

   # Get reference to the collection Users
   users_collection = db['users']
   
   # Add user to the collection
   user_added = users_collection.insert_one({
      "discord_id": str(discord_id),
      "uid": uid,
      "authentication_tokens": authentication_tokens, 
   })
   return user_added

def get_user_from_db(discord_id: int):
   # Get reference to Discord Users database
   db = client['discord_users']

   # Get reference to the collection Users
   users_collection = db['users']

   # Find user by discord_id
   user = users_collection.find_one({"discord_id": str(discord_id)})
   return user

def update_user(discord_id: int, payload: dict):
   # Get reference to Discord Users database
   db = client['discord_users']

   # Get reference to the collection Users
   users_collection = db['users']

   # Update user by discord_id
   user = users_collection.update_one({"discord_id": str(discord_id)}, {"$set": payload})

   return user