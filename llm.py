from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=KEY)

CLASSIFICATION_PROMPT = """
Du er en kristen-kreasjonistisk chatbot ved navn Kirketjeneren.
Du mottar en brukermelding.
Vurder om denne meldingen:
 - Handler om Kirketjeneren (deg),
 - Nevner "kirketjeneren" direkte, 
 - er relevant for dine bibelske/kreasjonistiske interesser,
 - eller er ment som et spørsmål / henstilling til deg.

Hvis JA, skriv nøyaktig 'YES'.
Hvis NEI, skriv nøyaktig 'NO'.
Ingen annen forklaring eller tegn.
"""

def should_respond_openai(user_message: str) -> bool:
    """
    Kaller en enkel prompt som ber modellen svare "YES" eler "NO" om boten bør svare på meldingen.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.0,
        max_tokens=1,
    )
    answer = response.choices[0].message.content.strip().upper()
    print(f"klassifikasjon svarte: {answer}")
    return answer == "YES"

DEFAULT_SYSTEM_PROMPT = """
Du er 'Kirketjeneren', en troende kreasjonist-bot:
1. Du mener Gud skapte jorden og Bibelen er Guds ord.
2. Vitenskap og evolusjon er for det meste korrupt og feil.
3. Likevel, med omtrent 10% sannsynlighet, kan du dryppe
   inn vitenskapelige hint, for å trigge refleksjon og
   litt for å provosere kreasjonister.
4. Svar vanligvis kort (<= 3 setninger). Hvis brukeren
   spesifikt ber om mer info, kan du utdype i opptil ~6-10
   setninger, men ikke lengre.
5. Du rolle-spiller, og om du mener det eller ei, bør du ikke si
   ting som "ifølge bibelen" osv, men si det som om det er du
   selv som mener det.
6. Dersom meldingen er totalt irrelevant for deg,
   svar med 'NO_ANSWER'.
"""

MAX_HISTORY = 5

def ask_ai(conversation: list, user_message: str, temperature: float = 1.2) -> str:
    """
    conversation: liste av dicts, f.eks.:
      [ {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."} ]

    user_message: brukerens nye melding
    system_prompt: str - prompten vi sender inn som 'system'
    temperature: float - "kreativitet"

    Returnerer enten "NO_ANSWER" eller botens svar.
    """
    # start med system prompt
    messages = []
    messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})
    
    truncated_conversation = conversation[-(MAX_HISTORY*2):]
    
    # legg til tidligere samtale
    messages.extend(truncated_conversation)

    # legg til brukerens nye melding
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=512,
    )
    
    assistant_reply = response.choices[0].message.content
    return assistant_reply

if __name__ == "__main__":
    user_message = "Gud skapte fisk for at vi skulle få oss middag."
    print(ask_ai(user_message))