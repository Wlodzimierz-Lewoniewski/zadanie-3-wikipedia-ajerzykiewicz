import urllib.request
import re
from urllib.parse import unquote

def pobierz_tresc_strony(url):
    fp = urllib.request.urlopen(url)
    tbytes = fp.read()
    txt = tbytes.decode("utf8")
    fp.close()
    return txt

def wyciagnij_linki_wewnetrzne(tresc, limit=5):
    linki_wewn = []
    for link in re.findall(r'a href="/wiki/([^":#]+)"', tresc):
        if ":" in link:  # Pomijanie linków do innych przestrzeni nazw
            continue
        linki_wewn.append(unquote(link).replace('_', ' '))
        if len(linki_wewn) >= limit:
            break
    return linki_wewn

def wyciagnij_url_obrazkow(tresc, limit=3):
    obrazki = re.findall(r'//upload\.wikimedia\.org[^"]+', tresc)
    return obrazki[:limit]

def wyciagnij_url_zrodel(tresc, limit=3):
    zrodla = re.findall(r'href="(http[^"]+)"', tresc)
    return zrodla[:limit]

def wyciagnij_kategorie(tresc, limit=3):
    kategorie = re.findall(r'title="Kategoria:([^"]+)"', tresc)
    return kategorie[:limit]

kat = input("Podaj nazwę kategorii w polskojęzycznej Wikipedii: ")
url_kategorii = "https://pl.wikipedia.org/wiki/Kategoria:" + kat.replace(" ", "_")

tresc_kategorii = pobierz_tresc_strony(url_kategorii)
adresy_artykulow = re.findall(r'a href="/wiki/([^":#]+)"', tresc_kategorii)
adresy_artykulow = list(dict.fromkeys(adresy_artykulow))  # Usunięcie duplikatów

wyniki = []
for i, adres in enumerate(adresy_artykulow[:2]):
    url_artykulu = "https://pl.wikipedia.org/wiki/" + adres
    tresc_artykulu = pobierz_tresc_strony(url_artykulu)

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

for wynik in wyniki:
    print("Artykuł:", wynik["artykul"])
    print("Linki wewnętrzne:", wynik["linki_wewnetrzne"])
    print("URL obrazków:", wynik["url_obrazkow"])
    print("URL źródeł:", wynik["url_zrodel"])
    print("Kategorie:", wynik["kategorie"])
    print("\n")
