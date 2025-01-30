import os
import json
import re
import random as rd
import discord as dc
from bible_api import get_random_verse

# hjelpefunksjon for å lese curses.json filen
def load_curses_data() -> dict:
    data_file = "curses.json"
    if not os.path.exists(data_file):
        return {}
    try:
        with open(data_file, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    
# returnerer en liste av (bruker, forbannelser), sortert synkende
def get_sorted_curses_desc() -> list:
    data = load_curses_data()
    return sorted(data.items(), key=lambda x: x[1], reverse=True)

# returnerer en liste av (bruker, forbannelser), sortert stigende
def get_sorted_curses_asc() -> list:
    data = load_curses_data()
    return sorted(data.items(), key=lambda x: x[1])


# Hjelpefunksjon for å lagre antall forbannelser per bruker, bruker JSON-fil curses-json til å persistere data
def update_curse_count(username: str, increment: int = 1) -> int:
    data_file = "curses.json"
    
    # lag fil om den ikkje eksisterer
    if not os.path.exists(data_file):
        with open(data_file, "w", encoding="utf-8-sig") as f:
            json.dump({}, f)
    
    # les inn data
    with open(data_file, "r", encoding="utf-8-sig") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
            
    # oppdater teller for bruker
    current_count = data.get(username, 0)
    new_count = current_count + increment if current_count + increment >= 0 else 0
    data[username] = new_count
    
    # skriv tilbake
    with open(data_file, "w", encoding="utf-8-sig") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return new_count

def get_response(message: dc.Message, user_input: str) -> str:
    lowered: str = user_input.lower()
    
    # tom input
    if lowered == "":
        return "Ikkje vær skremd for å lete den heilage ande leie deg. Snakk, mitt born."
    
    # 1) topp 5 forbennelser
    elif lowered.startswith("!topcurses"):
        sorted_data = get_sorted_curses_desc()
        if not sorted_data:
            return "Ingen forbannelser i databasen."
        top_5 = sorted_data[:5]
        response = ["## Topp 5 forbannelser:\n"]
        for i, (user, count) in enumerate(top_5, start=1):
            if i == 1:
                response.append(f":first_place: {user}: {count}")
            elif i == 2:
                response.append(f":second_place: {user}: {count}")
            elif i == 3:
                response.append(f":third_place: {user}: {count}")
            else:
                response.append(f"{i}. {user}: {count}")
        return "\n".join(response)
    
    # 2) laveste 5 forbannelser
    elif lowered.startswith("!lowestcurses"):
        sorted_data = get_sorted_curses_asc()
        if not sorted_data:
            return "Ingen forbannelser i databasen."
        bottom_5 = sorted_data[:5]
        response = ["## Laveste 5 forbannelser:\n"]
        for i, (user, count) in enumerate(bottom_5, start=1):
            if i == 1:
                response.append(f":first_place: {user}: {count}")
            elif i == 2:
                response.append(f":second_place: {user}: {count}")
            elif i == 3:
                response.append(f":third_place: {user}: {count}")
            else:
                response.append(f"{i}. {user}: {count}")
        return "\n".join(response)
    
    # 3) totalt antall forbannelser
    elif lowered.startswith("!totalcurses"):
        sorted_data = get_sorted_curses_desc()
        if not sorted_data:
            return "Ingen forbannelser i databasen."
        total_curses = sum(count for _, count in sorted_data)
        return f"Totalt antall forbannelser: {total_curses}"
    
    # 4) Sjekke forbannelser for en spesifikk eller egen bruker
    elif lowered.startswith("!curses"):
        if len(message.mentions) == 1:
            user = message.mentions[0].name
        else:
            user = message.author.name
        data = load_curses_data()
        count = data.get(user, 0)
        return f"{user} har {count} forbannelser."
    
    # hilsener
    elif any(phrase in lowered for phrase in ["hei", "hallo", "god dag", "god kveld", "god morgen"]):
        return rd.choice([
            "Vær helsa, guds born.",
            "Fred være med deg.",
            "Ha ein fotreffeleg dag, du som vandrar i tru og tvil."
            ])
        
    # forbannelse
    elif "forbann" in lowered:
        #trekk tilfeldig antall forbannelser
        cursed_amount = rd.randint(1, 100)
        # oppdater teller
        total_curses = update_curse_count(message.author.name, cursed_amount)
        response = f"Du forbanna {cursed_amount} menneskje. "
        response += f"Du har no forbanna {total_curses} menneskje i alt. " if total_curses > cursed_amount else ""
        response += "Måtte du finne frelse i Herrens ord."
        return response
    
    # tilgivelse
    elif any(phrase in lowered for phrase in ["tilgi", "tilgiv", "tilgje", "tilgev", "tilgjev", "angre", "beklager", "skriftemål", "angra"]):
        reduction = rd.randint(1, 20)
        new_total = update_curse_count(message.author.name, -reduction)
        data = load_curses_data()
        if reduction > data.get(message.author.name, 0):
            return (f"Høyr, du har nett vore i skriftemål. "
                    f"Du har no {new_total} forbanningar att.")
        return(f"Høyr, du har nett vore i skriftemål. "
               f"Med eit nådens slag har me tilgjeve deg {reduction} forbanningar. "
               f"Du har no {new_total} forbanningar att.")
    
    # Amen, halleluja, etc.
    elif any(phrase in lowered for phrase in ["amen", "halleluja", "pris herren"]):
        return rd.choice([
            "Amen, bror! Måtte du gå i fred.",
            "Halleluja! La all jorden lovsynge.",
            "Pris være Herrens skaperverk!"
        ])

    # Kreasjonisme / Big Bang / Darwin
    elif any(phrase in lowered for phrase in ["big bang", "darwin", "evolusjon", "urcella"]):
        return rd.choice([
            "Ver ikkje redd for tanken om evolusjon, men ver klar over Kven som skapte alt.",
            "Sjølv Darwin kan ikkje rikke ved den evige skaparkraft.",
            "Stor er kosmos, men større er underet ved at me kan forstå det."
        ])

    # Vitenskap, bevis
    elif any(phrase in lowered for phrase in ["vitenskap", "bevis", "forskning"]):
        return rd.choice([
            "Vitenskapen er berre vår måte å tyde Guds store bok på.",
            "Bevis og tru kan gå hand i hand, så lenge me ikkje gløymer kjelda til all sanning.",
            "Forskning er å grave i Herrens mektige verk, og alt me finn fortel om skaparverket."
        ])

    # Spørsmål om meningen med livet
    elif any(phrase in lowered for phrase in ["meningen med livet", "hva er meningen"]):
        return rd.choice([
            "Å leve i forundring og glede over alt som er skapt.",
            "Å elske sin neste, same kor vrang han kan vere.",
            "Kva er vel meining om ikkje å finne meining i det meiningslause?"
        ])
    
    # rettleiing
    elif any(phrase in lowered for phrase in ["rettleiing", "veiledning", "råd", "hjelp", "visdomsord", "vei", "sti"]):
        
        evolution_facts = [
            "Mennesket og sjimpansen delar rundt 98% av DNA-et.",
            "Alle levande artar har ein felles stamfar frå rundt 3,5 milliardar år sidan.",
            "Naturleg seleksjon er som ein blind klokkemakar, ifølge Richard Dawkins.",
            "Fuglar er etterkommarar av dinosaurar.",
            "Kosmos er 13,8 milliardar år gammal.",
            "Jorda er 4,5 milliardar år gammal."
        ]
            
        chance = rd.random()
        if chance < 0.9:
            return get_random_verse()
        else:
            return rd.choice(evolution_facts)

    # Ellers: generelle svar
    else:
        return rd.choice([
            "Eg er ikkje sikker på kva du meiner.",
            "Kva meiner du?",
            "Kan du utdjupe?",
            "Kva seier du?",
            "Kva meiner du med det?",
            "Eg forstår ikkje.",
            "Kan du forklare?",
            "Kva var det du kalla meg?",
            "Slik den allmektige har sagt: Uvisse er første steg mot visse.",
            "Det høyres ut som du treng ei openberring eller to.",
            "Sjølv paven kan ta feil – men han gjer det aldri, seier han.",
        ])
