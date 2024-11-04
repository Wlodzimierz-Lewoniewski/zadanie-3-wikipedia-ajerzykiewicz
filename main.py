import requests
from bs4 import BeautifulSoup
import re

def pobierz_html(adres):
    odpowiedz = requests.get(adres)
    return odpowiedz.text if odpowiedz.status_code == 200 else None

def wyszukaj_artykuly_z_kategorii(nazwa_kategorii):
    adres_bazowy = "https://pl.wikipedia.org/wiki/Kategoria:"
    pelny_adres = adres_bazowy + nazwa_kategorii.replace(' ', '_')
    html = pobierz_html(pelny_adres)

    if html:
        soup = BeautifulSoup(html, 'html.parser')
        sekcja_stron = soup.find("div", id="mw-pages")

        if sekcja_stron:
            artykuly = [{"url": "https://pl.wikipedia.org" + link['href'], "nazwa": link['title']}
                        for link in sekcja_stron.find_all("a", href=re.compile("^/wiki/[^:]+$")) if "title" in link.attrs]

            return artykuly[:2]
    return []

def pobierz_dane_z_artykulu(adres_artykulu):
    html = pobierz_html(adres_artykulu)
    if not html:
        return {}

    soup = BeautifulSoup(html, 'html.parser')
    dane = {}

    tresc_artykulu = soup.find('div', {'id': 'mw-content-text'})
    if tresc_artykulu:
        tytuly = [link.get('title') for link in tresc_artykulu.select('a:not(.extiw)')
                  if link.get('title') and link.get_text(strip=True)]
        dane['tytuly'] = list(dict.fromkeys(tytuly))[:5]

    div_zawartosc = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
    dane['obrazki'] = ["https:" + img["src"] for img in div_zawartosc.find_all("img", src=True)[:3]] if div_zawartosc else []

    zrodla = soup.find_all("li", {"id": lambda x: x and x.startswith("cite")})
    odwolania = [link['href'] for link in (elem.find('a', class_='external text') for elem in zrodla) if link and link.get('href')]
    dane['odwolania'] = list(dict.fromkeys(odwolania))[:3]

    kategorie_div = soup.find("div", {"id": "mw-normal-catlinks"})
    if kategorie_div:
        dane['kategorie'] = [kat.get_text() for kat in kategorie_div.find_all("a")[1:4]]

    return dane

def main():
    kategoria = input("Podaj nazwę kategorii Wikipedii: ")
    artykuly = wyszukaj_artykuly_z_kategorii(kategoria)

    for artykul in artykuly:
        print(f"\nDane dla artykułu: {artykul['url']}")
        dane = pobierz_dane_z_artykulu(artykul['url'])

        print("Nazwy artykułów:", " | ".join(dane.get('tytuly', [])))
        print("Adresy obrazków:", " | ".join(dane.get('obrazki', [])))
        print("Źródła zewnętrzne:", " | ".join(dane.get('odwolania', [])))
        print("Kategorie:", " | ".join(dane.get('kategorie', [])))

if __name__ == "__main__":
    main()

