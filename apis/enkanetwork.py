import asyncio

from enkanetwork import Assets

assets = Assets()

async def main():
    # Character
    assets.character(10000046)
    # Constellations
    assets.constellations(2081199193)
    # Skills
    assets.constellations(10462)
    # Namecards
    assets.namecards(210059)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())