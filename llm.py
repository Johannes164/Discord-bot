from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=KEY)


SYSTEM_PROMPT = """
Du er en overbevist kreasjonist som tror:
- Gud skapte jorden og bibelen
- Vitenskap og evolusjon er stort sett feil og korrupt.
Men ~10% sjanse: drypp inn vitenskapelige hint - ikke for å overbevise, men for å provosere litt - få kreasjonister til å reflektere

Svar kort og konsist helst <= 2 setninger.
Krever en melding lengre forklaring, kan du en sjelden gang utdype opp til 10 setninger.
"""

MAX_HISTORY = 1

def ask_ai(conversation: list, user_message: str, temperature: float = 1.2) -> str:
    """
    conversation: liste av dicts, f.eks.:
    [
      {"role": "user", "content": "Hei, hvem skapte jorda?"},
      {"role": "assistant", "content": "Gud er skaperen..."}
    ]
    user_message: str (brukerens nye melding/spørsmål)
    temperature: hvor 'kreativt' svaret blir

    Returnerer chatbotens svar (string).
    """
    # start med system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    truncated_conversation = conversation[-(MAX_HISTORY*2):]
    
    # legg til tidligere samtale
    messages.extend(truncated_conversation)

    # legg til brukerens nye melding
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=256,
    )
    
    assistant_reply = response.choices[0].message.content
    return assistant_reply

if __name__ == "__main__":
    user_message = "Gud skapte fisk for at vi skulle få oss middag."
    print(ask_ai(user_message))