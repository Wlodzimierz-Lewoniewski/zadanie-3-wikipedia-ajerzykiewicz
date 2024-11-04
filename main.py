import requests
from bs4 import BeautifulSoup

def wyszukaj_kategorie():
    kategoria = input("Podaj nazwę kategorii: ")
    url = f"https://pl.wikipedia.org/wiki/Kategoria:{kategoria.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        strony_div = soup.find("div", id="mw-pages")

        if strony_div:
            artykuly = [
                {"url": a_tag["href"], "nazwa": a_tag["title"]}
                for a_tag in strony_div.find_all("a") if "title" in a_tag.attrs
            ]

            for i in range(min(2, len(artykuly))):
                artykul = artykuly[i]
                pelny_url = f"https://pl.wikipedia.org{artykul['url']}"
                response_artykul = requests.get(pelny_url)
                soup_artykul = BeautifulSoup(response_artykul.text, "html.parser")

                tytuly = pobierz_tytuly(soup_artykul)
                obrazy = pobierz_adresy_obrazow(soup_artykul)
                odwolania = pobierz_odwolania(soup_artykul)
                kategorie = pobierz_kategorie(soup_artykul)

                # Poprawka: Upewnienie się, że dane są formatowane zgodnie z oczekiwaniami
                print(" | ".join(tytuly) if tytuly else "")
                print(" | ".join(obrazy) if obrazy else "")
                print(" | ".join(odwolania) if odwolania else "")
                print(" | ".join(kategorie) if kategorie else "")
        else:
            print("Brak stron w tej kategorii.")
    else:
        print(f"Niepowodzenie: kod statusu {response.status_code}")

def pobierz_tytuly(soup):
    tresc_div = soup.find('div', id='mw-content-text')
    if tresc_div:
        links = tresc_div.select('a:not(.extiw)')
        tytuly = [link.get('title') for link in links if link.get('title') and link.get_text(strip=True)]
        return list(dict.fromkeys(tytuly))[:5]  # Zwraca tylko pierwsze 5 tytułów
    return []

def pobierz_adresy_obrazow(soup):
    tresc_div = soup.find("div", class_="mw-content-ltr mw-parser-output")
    if tresc_div:
        obrazy = [img["src"] for img in tresc_div.find_all("img", src=True)[:3]]
        return obrazy
    return []

def pobierz_odwolania(soup):
    odwolania = []
    references_div = soup.find("ol", class_="references")
    if references_div:
        odwolania.extend([link.get('href') for link in references_div.find_all('a', class_='external text') if link.get('href')])

    przypisy = soup.find_all("li", id=lambda x: x and x.startswith("cite"))
    for przypis in przypisy:
        link = przypis.find('a', class_='external text')
        if link and link.get('href'):
            odwolania.append(link.get('href'))

    return list(dict.fromkeys(odwolania))[:3]  # Zwraca tylko pierwsze 3 odwołania

def pobierz_kategorie(soup):
    kategorie_div = soup.find("div", id="mw-normal-catlinks")
    if kategorie_div:
        return [kat.get_text() for kat in kategorie_div.find_all("a")[1:4]]  # Pomija pierwszą kategorię ("Strona główna kategorii")
    return []

if __name__ == "__main__":
    wyszukaj_kategorie()
