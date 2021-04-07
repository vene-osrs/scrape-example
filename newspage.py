import requests
import time
from bs4 import BeautifulSoup
from helpers import format_log


class NewsPage:
    start_time = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.90 Safari/537.36',
    }
    url = None
    source = None
    soup = None
    country = None
    file = None
    source_id = None
    db_articles = None
    new_articles = []
    database = None

    def __init__(self):
        pass

    def add_new_article(self, title, content, url, published_at, headline="", author="", category="", language="",
                        image_url=""):
        article = [None, self.source_id, title, headline, content, author, category, language, url, image_url,
                   published_at]
        self.new_articles.append(article)

    def visit_main_url(self, parse_type='lxml'):
        try:
            self.source = requests.get(self.url, headers=self.headers).content
            self.soup = BeautifulSoup(self.source, parse_type)
            format_log("--- %s took %s seconds ---" % (__name__, time.time() - self.start_time))
        except:
            format_log("-- ERROR in %s visiting main url (ID: %s) --" % (__name__, self.source_id))

    def get_url_content(self, url, parse_type='lxml'):
        try:
            source = requests.get(url, headers=self.headers).content
            soup = BeautifulSoup(source, parse_type)
            format_log("--- %s took %s seconds ---" % (__name__, time.time() - self.start_time))
            return soup
        except:
            format_log("-- ERROR in %s retrieving content (ID: %s) --" % (__name__, self.source_id))
