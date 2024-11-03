import requests
from bs4 import BeautifulSoup
import re

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Błąd podczas pobierania strony {url}: {response.status_code}")
        return None

def extract_articles_from_category(category):
    base_url = "https://pl.wikipedia.org/wiki/Kategoria:"
    category_url = base_url + category.replace(" ", "_")
    html = get_html(category_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        mw_pages_div = soup.find("div", id="mw-pages")
        articles = []
        if mw_pages_div:
            links = mw_pages_div.find_all("a", href=re.compile("^/wiki/[^:]+$"))
            for link in links[:2]:  # Pobieramy maksymalnie 2 artykuły
                article_url = "https://pl.wikipedia.org" + link['href']
                article_name = link.get_text()
                articles.append({"url": article_url, "name": article_name})
        return articles
    return []

def extract_data_from_article(article):
    url = article['url']
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # Ekstrakcja odnośników wewnętrznych
    article_links = soup.find_all('a', href=re.compile("^/wiki/[^:#]+$"))
    article_names = [link.get_text().strip() for link in article_links[:5] if link.get_text().strip()]

    # Ekstrakcja URL obrazków
    images = soup.find_all('img', src=True)
    image_urls = ["https:" + img['src'] for img in images[:3] if img['src'].startswith("//upload.wikimedia.org")]

    # Ekstrakcja źródeł zewnętrznych
    external_links = soup.find_all('a', href=re.compile("^https?://"))
    external_urls = [link['href'] for link in external_links[:3] if link['href']]

    # Ekstrakcja nazw kategorii
    category_div = soup.find("div", {"id": "mw-normal-catlinks"})
    category_names = [cat.get_text().strip() for cat in category_div.find_all("a")[1:4]] if category_div else []

    return {
        "article_names": article_names,
        "image_urls": image_urls,
        "external_urls": external_urls,
        "category_names": category_names
    }

def main():
    category = input("Podaj nazwę kategorii Wikipedii: ")
    articles = extract_articles_from_category(category)

    if not articles:
        print("Nie znaleziono artykułów w tej kategorii lub wystąpił błąd.")
        return

    for article in articles:
        print(f"\nDane dla artykułu: {article['name']} ({article['url']})")
        data = extract_data_from_article(article)
        if data:
            print("Nazwy artykułów (odn. wewnętrzne):", " | ".join(data['article_names']))
            print("Adresy URL obrazków:", " | ".join(data['image_urls']))
            print("Adresy URL źródeł (zewnętrzne):", " | ".join(data['external_urls']))
            print("Kategorie:", " | ".join(data['category_names']))
        else:
            print("Nie udało się pobrać danych z artykułu.")

if __name__ == "__main__":
    main()
