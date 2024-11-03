import requests
from bs4 import BeautifulSoup
import re

# Funkcja do pobierania HTML danej strony z odpowiednim nagłówkiem User-Agent
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Błąd podczas pobierania strony {url}: {response.status_code}")
        return None

# Funkcja do ekstrakcji artykułów z kategorii Wikipedii
def extract_articles_from_category(category):
    base_url = "https://pl.wikipedia.org/wiki/Kategoria:"
    category_url = base_url + category.replace(" ", "_")
    html = get_html(category_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        # Szukamy odnośników do artykułów w kategorii
        article_links = soup.find_all('a', href=re.compile("^/wiki/[^:]+$"))
        articles = []
        for link in article_links[:2]:  # Pobieramy pierwsze 2 unikalne artykuły
            url_article = "https://pl.wikipedia.org" + link['href']
            if url_article not in articles:
                articles.append(url_article)
        return articles
    return []

# Funkcja do ekstrakcji danych z artykułu
def extract_data_from_article(url):
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # Ekstrakcja nazw artykułów z odnośników wewnętrznych
    article_links = soup.find_all('a', href=re.compile("^/wiki/[^:#]+$"))
    article_names = [link.get_text().strip() for link in article_links[:5] if link.get_text().strip()]

    # Ekstrakcja URL obrazków
    images = soup.find_all('img', src=True)
    image_urls = ["https:" + img['src'] for img in images[:3] if img['src'].startswith("//upload.wikimedia.org")]

    # Ekstrakcja źródeł zewnętrznych (odnośniki zewnętrzne)
    external_links = soup.find_all('a', href=re.compile("^https?://"))
    external_urls = [link['href'] for link in external_links[:3] if link['href']]

    # Ekstrakcja kategorii przypisanych do artykułu
    categories = soup.find_all('a', href=re.compile("^/wiki/Kategoria:"))
    category_names = [category.get_text().strip() for category in categories[:3] if category.get_text().strip()]

    return {
        "article_names": article_names,
        "image_urls": image_urls,
        "external_urls": external_urls,
        "category_names": category_names
    }

# Funkcja główna wykonująca zadanie
def main():
    category = input("Podaj nazwę kategorii Wikipedii: ")
    articles = extract_articles_from_category(category)

    if not articles:
        print("Nie znaleziono artykułów w tej kategorii lub wystąpił błąd.")
        return

    for article_url in articles:
        print(f"\nDane dla artykułu: {article_url}")
        data = extract_data_from_article(article_url)
        if data:
            print("Nazwy artykułów (odn. wewnętrzne):", data['article_names'])
            print("Adresy URL obrazków:", data['image_urls'])
            print("Adresy URL źródeł (zewnętrzne):", data['external_urls'])
            print("Kategorie:", data['category_names'])
        else:
            print("Nie udało się pobrać danych z artykułu.")

if __name__ == "__main__":
    main()
