import requests
from bs4 import BeautifulSoup

def format_output(elements, delimiter=" | "):
    return delimiter.join(elements)

wiki_name = input()
wiki_name = wiki_name.replace(" ", "_")
url = "https://pl.wikipedia.org/wiki/Kategoria:" + wiki_name
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    mw_pages_div = soup.find("div", id="mw-pages")

    if mw_pages_div:
        articles = []
        links = mw_pages_div.find_all("a")

        for link in links:
            if "title" in link.attrs:
                article_url = link["href"]
                article_name = link["title"]
                articles.append({"url": article_url, "name": article_name})

        for i in range(2):
            if i < len(articles):
                article = articles[i]
                article_url = "https://pl.wikipedia.org" + article["url"]
                article_response = requests.get(article_url)
                article_soup = BeautifulSoup(article_response.text, "html.parser")
                titles = []
                div_container = article_soup.find('div', {'id': 'mw-content-text', 'class': 'mw-body-content'})

                if div_container:
                    links = div_container.select('a:not(.extiw)')
                    for link in links:
                        title = link.get('title')
                        text = link.get_text(strip=True)
                        if title and text:
                            titles.append(title)
                            if len(titles) == 5:
                                break

                content_text_div = article_soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
                images = content_text_div.find_all("img", src=True) if content_text_div else []
                image_urls = [img["src"] for img in images[:3]]

                h2_przypisy = article_soup.find('span', {"id": "Przypisy"})
                if h2_przypisy:
                    references = h2_przypisy.find_next("ol", {"class": "references"})
                    external_links = references.find_all('a', {"class": 'external text'}) if references else []
                    reference_urls = [link['href'].replace("&", "&amp;") for link in external_links[:3]]
                else:
                    reference_urls = []

                categories = article_soup.find("div", {"id": "mw-normal-catlinks"})
                category_names = [cat.get_text() for cat in categories.find_all("a")[1:4]] if categories else []

                formatted_title = format_output(titles)
                formatted_image_url = format_output(image_urls)
                formatted_reference_url = format_output(reference_urls)
                formatted_category_name = format_output(category_names)

                print(formatted_title)
                print(formatted_image_url)
                print(formatted_reference_url)
                print(formatted_category_name)
            else:
                print(f"Article {i + 1}: No information")
    else:
        print("No mw-pages div")
else:
    print(f"Status code: {response.status_code}")
