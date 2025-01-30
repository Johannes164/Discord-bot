import os
from dotenv import load_dotenv
import discord as dc
from discord.ext import commands
from responses import get_response
from llm import ask_ai
import random as rd
from datetime import datetime
import json

# Laster token fra .env
load_dotenv()
TOKEN: str = os.getenv('DISCORD_TOKEN')

# Bot setup
intents: dc.Intents = dc.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_bot_message_id = None
memory = {}
log_file = None

# bot er klar
@bot.event
async def on_ready():
    print("Initialiserer logging...")
    init_logging()
    print("Loggin initialisert!\n")

    log("------------------------------------------------")
    log(f"Bot '{bot.user}' har koblet til Discord!")
    print(f'{bot.user} har koblet til Discord!')
    log("Starter lasting av memory...")

    load_memory()

    # Prøv å laste extension commands
    try:
        await bot.load_extension("commands")
        log("commands.py lastet inn!")
        print("commands.py lastet inn!")
    except Exception as e:
        log(f"Feil under lasting av commands: {e}")
        print(f"Feil under synkronisering: {e}")

    try:
        synced = await bot.tree.sync()
        log(f"Synkroniserte {len(synced)} kommando(er)")
        print(f"Synkroniserte {len(synced)} kommando(er)")
    except Exception as e:
        log(f"Feil under synkronisering: {e}")
        print(f"Feil under synkronisering: {e}")
    
    
    log("------------------------------------------------\n")
        


# Meldingsfunksjonalitet
@bot.event
async def on_message(message: dc.Message) -> None:
    global last_bot_message_id

    # Logg innkommende melding
    log(f"Kanal: [#{message.channel.name}] | Forfatter: {message.author} | Melding:\n{message.content}")
    if message.author == bot.user:
        return
    
    #if str(message.channel.id) != "1333525486747521095" and bot.user not in message.mentions:
    #    return
    
    should_respond = rd.random() < 0.15
    
    mentioned = bot.user in message.mentions
    replying_to_bot = (
        message.reference and
        message.reference.message_id == last_bot_message_id
    )
    
    # sjekk om det er en referanse til en tidligere melding
    referenced_message = await get_referenced_message(message)
    
    if referenced_message:
        user_input = f"Bruker refererer til:\n{referenced_message.content}\n\nBrukerens melding:\n{message.content}"
        log(f"Fant referanse i meldingen: {referenced_message.id}\nMeldingen som refereres til: {referenced_message.content}\n")
    else:
        user_input = message.content
        
    if mentioned or replying_to_bot or referenced_message or should_respond:
        # kall AI
        bot_reply = ask_ai(
            conversation=memory.get("messages", []),
            user_message=user_input,
            temperature=1.2
        )
        
        # legg til i memory
        # 1) brukermelding
        memory.setdefault("messages", []).append({"role": "user", "content": user_input}) 
        # 2) botsvar
        memory["messages"].append({"role": "assistant", "content": bot_reply})
        save_memory()
        
        log(f"AI input: \"\n{user_input}\n\"\n")
        log(f"AI output: \"\n{bot_reply}\n\"\n")
    
        sent_message = await message.channel.send(bot_reply)
        last_bot_message_id = sent_message.id
        
#    await send_message(message, user_message)
    
    
#async def send_message(message: dc.Message, user_message: str) -> None:
#    if not user_message:
#        print("Melding var tom. Kanskje intents ikke er satt opp riktig?")
#        return
#    
#    if is_private := user_message[0] == "?":
#        user_message = user_message[1:]
#    
#    try:
#        response: str = get_response(message, user_message)
#        await message.author.send(response) if is_private else await message.channel.send(response)
#    except Exception as e:
#        print(e)

def load_memory():
    """Laster samtalehistorikk fra memory.json hvis den finnes."""
    global memory
    if os.path.exists("memory.json"):
        try:
            with open("memory.json", "r", encoding="utf-8-sig") as f:
                memory = json.load(f)
            log("Memory lastet fra memory.json")
        except Exception as e:
            log(f"Feil ved lasting av memory.json: {e}")
            memory = {}
    else:
        log("Fant ikke memory.json, starter med tomt minne")
        memory = {}
        
def save_memory():
    """Lagrer samtalehistorikk til memory.json."""
    try:
        with open("memory.json", "w", encoding="utf-8-sig") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        log("Input/Output lagret til memory.json")
    except Exception as e:
        log(f"Feil ved lagring av memory.json: {e}")
        
def init_logging():
    """Oppretter en loggfil."""
    global log_file
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/botlog_{timestamp}.txt"
    log_file = open(filename, "w", encoding="utf-8")
    
def log(text: str):
    """Skriver en linje til loggfilen og flusher."""
    global log_file
    if log_file is None:
        print("Loggfil ikke initialisert!")
        return
    log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
    global logtab
    logtab = "                    - "
    log_file.flush() # Tvinger skriving til disk

async def get_referenced_message(message: dc.Message):
    """Sjekker reply eller Discord-lenke for å finne en tidligere melding"""
    if message.reference and message.reference.message_id:
        try:
            return await message.channel.fetch_message(message.reference.message_id)
        except dc.NotFound:
            return None
    
    for word in message.content.split():
        if word.startswith("https://discord.com/channels/"):
            try:
                parts = word.split("/")
                guild_id = int(parts[4])
                channel_id = int(parts[5])
                message_id = int(parts[6])
                
                if guild_id == message.guild.id and channel_id == message.channel.id:
                    return await message.channel.fetch_message(message_id)
            except (IndexError, ValueError):
                pass # Ignorerer ugyldige lenker
    return None # Ingen referanse funnet
                    
# main entry point
def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()