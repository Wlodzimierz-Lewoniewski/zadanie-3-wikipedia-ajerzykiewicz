import requests
from bs4 import BeautifulSoup
import re

# Funkcja do pobierania treści strony z odpowiednim nagłówkiem
def fetch_html_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    print(f"Nie udało się pobrać strony: {url} (Status code: {response.status_code})")
    return None

# Funkcja do uzyskiwania artykułów z danej kategorii Wikipedii
def get_articles_from_category(category):
    base_url = "https://pl.wikipedia.org/wiki/Kategoria:"
    category_url = base_url + category.replace(" ", "_")
    html_content = fetch_html_content(category_url)
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        # Szukanie linków do artykułów w kategorii
        mw_pages_div = soup.find("div", id="mw-pages")
        if mw_pages_div:
            links = mw_pages_div.find_all("a", href=re.compile("^/wiki/[^:]+$"))
            for link in links[:2]:  # Pobieranie do dwóch artykułów
                article_url = "https://pl.wikipedia.org" + link['href']
                articles.append({"url": article_url, "name": link.get_text()})
        return articles
    return []

# Funkcja do wyodrębniania danych z artykułu
def extract_article_data(article):
    url = article['url']
    html_content = fetch_html_content(url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Wyciąganie odnośników wewnętrznych
    internal_links = soup.find_all('a', href=re.compile("^/wiki/[^:#]+$"))
    internal_article_names = [link.get_text().strip() for link in internal_links[:5] if link.get_text().strip()]

    # Wyciąganie adresów URL obrazków
    images = soup.find_all('img', src=True)
    image_urls = ["https:" + img['src'] for img in images[:3] if img['src'].startswith("//upload.wikimedia.org")]

    # Wyciąganie zewnętrznych odnośników
    external_links = soup.find_all('a', href=re.compile("^https?://"))
    external_urls = [link['href'] for link in external_links[:3] if link['href']]

    # Wyciąganie kategorii
    category_div = soup.find("div", id="mw-normal-catlinks")
    category_names = [cat.get_text().strip() for cat in category_div.find_all("a")[1:4]] if category_div else []

    return {
        "article_names": internal_article_names,
        "image_urls": image_urls,
        "external_urls": external_urls,
        "category_names": category_names
    }

# Funkcja główna
def main():
    category = input("Podaj nazwę kategorii Wikipedii: ")
    articles = get_articles_from_category(category)

    if not articles:
        print("Nie znaleziono artykułów w tej kategorii lub wystąpił błąd.")
        return

    for article in articles:
        print(f"\nDane dla artykułu: {article['name']} ({article['url']})")
        data = extract_article_data(article)
        if data:
            print("Nazwy artykułów (odnośniki wewnętrzne):", " | ".join(data['article_names']))
            print("Adresy URL obrazków:", " | ".join(data['image_urls']))
            print("Adresy URL źródeł (odnośniki zewnętrzne):", " | ".join(data['external_urls']))
            print("Kategorie:", " | ".join(data['category_names']))
        else:
            print("Nie udało się pobrać danych z artykułu.")

if __name__ == "__main__":
    main()
