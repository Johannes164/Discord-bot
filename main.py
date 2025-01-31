import os
from dotenv import load_dotenv
import discord as dc
from discord.ext import commands
import llm
import random as rd
import datetime as dt
import json
import re

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
mute_until = None

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
    
    if handle_mute(message.content):
        return
    
    if mute_until and dt.datetime.now() < mute_until:
        return

    # Logg innkommende melding
    log(f"Kanal: [#{message.channel.name}] | Forfatter: {message.author} | Melding:\n{message.content}")
    if message.author == bot.user:
        return
    
    # Sjekk triggere
    mentioned = bot.user in message.mentions
    replying_to_bot = (
        message.reference and
        message.reference.message_id == last_bot_message_id
    )
    random_trigger = (rd.random() < 0.15) # 15% sjanse for å svare uavhengig av andre triggere
    
    # sjekk om det er en referanse til en tidligere melding
    referenced_message = await get_referenced_message(message)
    referencing_bot = False
    if referenced_message and referenced_message.author == bot.user:
        referencing_bot = True
        
    respond = False
    respond_reason = None
    
    if mentioned:
        respond = True
        respond_reason = "mention"
    elif replying_to_bot:
        respond = True
        respond_reason = "reply_to_bot"
    elif referencing_bot:
        respond = True
        respond_reason = "reference_bot"
    elif random_trigger:
        respond = True
        respond_reason = "random_chance"
    else:
        respond_reason = "classification"
        classification_result = llm.should_respond_openai(message.content)
        log(f"Klassifisering fra LLM: {classification_result}")
        
        respond = classification_result
        if respond:
            respond_reason = "classification=YES"
        else:
            respond_reason = "classification=NO"
            
        
    if respond:
        if referencing_bot:
            user_input = f"(Referanse til botens tidligere melding)\n{message.content}"
        else:
            user_input = message.content
            
        bot_reply = llm.ask_ai(
            conversation=memory.get("messages", []),
            user_message=user_input,
            temperature=1.2
        )
    
        if bot_reply.upper() == "NO_ANSWER":
            log(f"AI returnerte NO_ANSWER, avbryter.")
            return
        
        # legg til i memory
        memory.setdefault("messages", []).append({"role": "user", "content": user_input})
        memory["messages"].append({"role": "assistant", "content": bot_reply})
        save_memory()
        
        log(f"Trigger: {respond_reason}")
        log(f"AI input: \"\n{user_input}\n\"\n")
        log(f"AI output: \"\n{bot_reply}\n\"\n")
        
        sent_message = await message.channel.send(bot_reply)
        last_bot_message_id = sent_message.id
        
def handle_mute(content: dc.Message) -> bool:
    global mute_until
    match = re.match(r"^Mute (\d+)([mh])$", content.strip(), re.IGNORECASE) # sjekker om meldingen er "Mute <tall><m/h>". 
    if match:
        amount, unit = int(match.group(1)), match.group(2).lower()
        duration = dt.timedelta(minutes=amount) if unit == "m" else dt.timedelta(hours=amount)
        
        if amount == 0:
            mute_until = None
            log("Botten er ikke lenger mutet.")
        else:
            mute_until = dt.datetime.now() + duration
            log(f"Botten er mutet til {mute_until.strftime('%Y-%m-%d %H:%M:%S')}.")
            
        return True
    return False

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
        
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/botlog_{timestamp}.txt"
    log_file = open(filename, "w", encoding="utf-8-sig")
    
def log(text: str):
    """Skriver en linje til loggfilen og flusher."""
    global log_file
    if log_file is None:
        print("Loggfil ikke initialisert!")
        return
    log_file.write(f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {text}\n") # "                    - "
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