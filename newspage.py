import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from helpers import format_log
from os import path


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
    custom_url = None
    custom_url_article_id = None

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

    def update_existing_article(self, content):
        # Logic will be added later.
        pass

    def get_bs_object(self, html, parse_type=None):
        if parse_type is not None:
            return BeautifulSoup(html, parse_type)

        return BeautifulSoup(html)

    def store_xls(self, source_provider):
        # https://stackoverflow.com/questions/51394261/python-access-second-element-of-list
        empty_fields = [item[0] for item in self.new_articles]
        source_ids = [item[1] for item in self.new_articles]
        titles = [item[2] for item in self.new_articles]
        headlines = [item[3] for item in self.new_articles]
        descriptions = [item[4] for item in self.new_articles]
        authors = [item[5] for item in self.new_articles]
        categories = [item[6] for item in self.new_articles]
        languages = [item[7] for item in self.new_articles]
        links = [item[8] for item in self.new_articles]
        img_urls = [item[9] for item in self.new_articles]
        dates = [item[10] for item in self.new_articles]

        s1 = pd.Series(titles, name='Title')
        s2 = pd.Series(headlines, name='Headline')
        s3 = pd.Series(descriptions, name='Text')
        s4 = pd.Series(authors, name='Author')
        s5 = pd.Series(categories, name='Category')
        s6 = pd.Series(languages, name='Language')
        s7 = pd.Series(links, name='Link')
        s8 = pd.Series(img_urls, name='Image')
        s9 = pd.Series(dates, name='Date')

        df1 = pd.concat([s1, s2, s3, s4, s5, s6, s7, s8, s9], axis=1)
        df = df1.dropna()

        with pd.ExcelWriter(f"{path.splitext(source_provider)[0]}.xlsx", engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
