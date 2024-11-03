import urllib.request
import re
from urllib.parse import unquote

def pobierz_tresc_strony(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as fp:
            tbytes = fp.read()
        txt = tbytes.decode('utf-8')
        return txt
    except Exception as e:
        print(f"Błąd podczas pobierania treści strony: {e}")
        return ""

# Funkcja do wyciągania linków wewnętrznych z artykułu
def wyciagnij_linki_wewnetrzne(tresc, limit=5):
    linki_wewn = []
    try:
        for link in re.findall(r'<a href="/wiki/([^":#]+)"', tresc):
            if ":" in link:  # Pomijanie linków do innych przestrzeni nazw
                continue
            linki_wewn.append(unquote(link).replace('_', ' '))
            if len(linki_wewn) >= limit:
                break
    except Exception as e:
        print(f"Błąd podczas wyciągania linków wewnętrznych: {e}")
    return linki_wewn

# Funkcja do wyciągania URL-ów obrazków
def wyciagnij_url_obrazkow(tresc, limit=3):
    obrazki = []
    try:
        obrazki = re.findall(r'//upload\.wikimedia\.org[^"]+', tresc)
    except Exception as e:
        print(f"Błąd podczas wyciągania URL-ów obrazków: {e}")
    return obrazki[:limit]

# Funkcja do wyciągania URL-ów źródeł zewnętrznych
def wyciagnij_url_zrodel(tresc, limit=3):
    zrodla = []
    try:
        zrodla = re.findall(r'href="(http[^"]+)"', tresc)
    except Exception as e:
        print(f"Błąd podczas wyciągania URL-ów źródeł: {e}")
    return zrodla[:limit]

# Funkcja do wyciągania nazw kategorii
def wyciagnij_kategorie(tresc, limit=3):
    kategorie = []
    try:
        kategorie = re.findall(r'title="Kategoria:([^"]+)"', tresc)
    except Exception as e:
        print(f"Błąd podczas wyciągania kategorii: {e}")
    return kategorie[:limit]

# Pobranie nazwy kategorii od użytkownika
kat = input("Podaj nazwę kategorii w polskojęzycznej Wikipedii: ")

# Budowanie URL do kategorii
url_kategorii = "https://pl.wikipedia.org/wiki/Kategoria:" + kat.replace(" ", "_")

# Pobranie i analiza treści strony kategorii
tresc_kategorii = pobierz_tresc_strony(url_kategorii)
adresy_artykulow = re.findall(r'<a href="/wiki/([^":#]+)"', tresc_kategorii)
adresy_artykulow = list(dict.fromkeys(adresy_artykulow))  # Usunięcie duplikatów

# Pobranie i analiza pierwszych dwóch artykułów
wyniki = []
for i, adres in enumerate(adresy_artykulow[:2]):
    url_artykulu = "https://pl.wikipedia.org/wiki/" + adres
    tresc_artykulu = pobierz_tresc_strony(url_artykulu)

    # Wyciąganie danych
    linki_wewn = wyciagnij_linki_wewnetrzne(tresc_artykulu)
    url_obrazkow = wyciagnij_url_obrazkow(tresc_artykulu)
    url_zrodel = wyciagnij_url_zrodel(tresc_artykulu)
    kategorie = wyciagnij_kategorie(tresc_artykulu)

    wyniki.append({
        "artykul": adres.replace('_', ' '),
        "linki_wewnetrzne": linki_wewn,
        "url_obrazkow": url_obrazkow,
        "url_zrodel": url_zrodel,
        "kategorie": kategorie
    })

# Wyświetlanie wyników
for wynik in wyniki:
    print("\nArtykuł:", wynik["artykul"])
    print("Linki wewnętrzne:", wynik["linki_wewnetrzne"])
    print("URL obrazków:", wynik["url_obrazkow"])
    print("URL źródeł:", wynik["url_zrodel"])
    print("Kategorie:", wynik["kategorie"])
