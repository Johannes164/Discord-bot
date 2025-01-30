from dotenv import load_dotenv
import os
import requests
import random
from bs4 import BeautifulSoup

# Last inn miljøvariabler
load_dotenv()
API_KEY = os.getenv('BIBLE_API_KEY')
BASE_URL = "https://api.scripture.api.bible/v1"
BIBLE_ID = "246ad95eade0d0a1-01"  # ID for Biblica® Open Norwegian Living New Testament

# Headers for forespørsler
headers = {
    "api-key": API_KEY,
    "Accept": "application/json"
}

def get_books():
    # Henter alle bøker i Bibelen
    response = requests.get(f"{BASE_URL}/bibles/{BIBLE_ID}/books", headers=headers)
    if response.status_code == 200:
        all_books = response.json()["data"]
        valid_books = []
        
        for book in all_books:
            book_id = book["id"]
            chapters_response = requests.get(f"{BASE_URL}/bibles/{BIBLE_ID}/books/{book_id}/chapters", headers=headers)
            
            if chapters_response.status_code == 200 and chapters_response.json()["data"]:
                valid_books.append(book)
                
        return valid_books
    else:
        raise Exception(f"Failed to fetch books: {response.status_code} - {response.text}")

def get_chapters(book_id):
    # Henter kapitler for en bestemt bok
    response = requests.get(f"{BASE_URL}/bibles/{BIBLE_ID}/books/{book_id}/chapters", headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"Failed to fetch chapters: {response.status_code} - {response.text}")

def get_verses(chapter_id):
    # Henter vers i et bestemt kapittel
    response = requests.get(f"{BASE_URL}/bibles/{BIBLE_ID}/chapters/{chapter_id}/verses", headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"Failed to fetch verses: {response.status_code} - {response.text}")

def get_random_verse():
    cleaned_content = ""
    while len(cleaned_content) < 50:
        # Velg en tilfeldig bok
        books = get_books()
        random_book = random.choice(books)
        book_id = random_book["id"]

        # Velg et tilfeldig kapittel fra boken
        chapters = get_chapters(book_id)
        random_chapter = random.choice(chapters)
        chapter_id = random_chapter["id"]

        # Velg et tilfeldig vers fra kapittelet
        verses = get_verses(chapter_id)
        random_verse = random.choice(verses)
        
        # Hent teksten for det tilfeldige verset
        verse_id = random_verse["id"]
        response = requests.get(f"{BASE_URL}/bibles/{BIBLE_ID}/verses/{verse_id}", headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch verse text: {response.status_code} - {response.text}")
        verse_data = response.json()["data"]
        
        reference = verse_data["reference"]
        raw_content = verse_data["content"]
        
        # Fjern HTML-taggene fra innholdet
        soup = BeautifulSoup(raw_content, "html.parser")
        for span in soup.find_all("span", class_="v"):
            span.decompose()
        cleaned_content = soup.get_text(separator=" ")
        
    return {
        "reference": reference,
        "content": cleaned_content
    }


# Hent et tilfeldig bibelvers
if __name__ == "__main__":
    for _ in range(5):
        try:
            random_verse = get_random_verse()
            print("Tilfeldig vers:")
            print(random_verse)
        except Exception as e:
            print(e)
