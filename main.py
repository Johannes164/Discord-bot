import os
from dotenv import load_dotenv
import discord as dc
from discord.ext import commands
from responses import get_response

# Laster token fra .env
load_dotenv()
TOKEN: str = os.getenv('DISCORD_TOKEN')

# Bot setup
intents: dc.Intents = dc.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# bot er klar
@bot.event
async def on_ready():
    print(f'{bot.user} har koblet til Discord!')
    
    try:
        await bot.load_extension("commands")
        print("commands.py lastet inn!")
    except Exception as e:
        print(f"Feil under synkronisering: {e}")
        
    try:
        synced = await bot.tree.sync()
        print(f"Synkroniserte {len(synced)} kommando(er)")
    except Exception as e:
        print(f"Feil under synkronisering: {e}")


# Meldingsfunksjonalitet
@bot.event
async def on_message(message: dc.Message) -> None:
    if message.author == bot.user:
        return
    
    if str(message.channel.id) != "1333525486747521095" and bot.user not in message.mentions:
        return
    username: str = message.author.name
    user_message: str = message.content
    channel: str = message.channel.name
    
    print(f"[{channel}] {username}: \"{user_message}\"")
    await send_message(message, user_message)
    
    
async def send_message(message: dc.Message, user_message: str) -> None:
    if not user_message:
        print("Melding var tom. Kanskje intents ikke er satt opp riktig?")
        return
    
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]
    
    try:
        response: str = get_response(message, user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# main entry point
def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()