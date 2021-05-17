from datetime import datetime
from pytz import timezone, utc as time_utc
from time import strptime
from newspage import NewsPage


# UPDATE THE CLASS TO THE WEBSITE NAME, SIMILAR AS THIS ONE
class RacunalniskeNovice:
    news_page = None
    timezone = timezone("Europe/Ljubljana")  # Make sure to use correct timezone! Usually its Europe/London for UTC.

    def __init__(self):
        self.news_page = NewsPage()
        self.news_page.url = 'https://racunalniske-novice.com/feed/'

    # This is only used to get the text from url.
    # IT MUST EXIST!
    # It can also be used to run it separately from 'parse_article' to get the article content.
    def parse_text_content(self, article_link_soup, url=None):
        if url is not None:
            article_link_soup = self.news_page.get_url_content(url)

        article_content = ""
        if article_link_soup:
            content_soap = article_link_soup.find('div', class_='summary')
            article_content = content_soap.get_text() + " "
            content_soap_two = article_link_soup.find('div', class_='content')
            if content_soap_two:
                for p in content_soap_two.find_all('p'):
                    article_content += p.get_text() + " "

        return article_content

    # Logic to parse stuff happens here.
    def parse_article_data(self, article):
        language = "slovenščina"  # Can be hardcoded
        url = article.link.get_text()
        title = article.title.get_text(strip=True)
        description = article.description.get_text(strip=True)
        description = self.news_page.get_bs_object(description, 'lxml').get_text(strip=True)
        category = ""
        categories = article.findAll('category')
        for c in categories:
            category += c.get_text(strip=True) + " / "

        category = category[:-2]
        url_to_image = article.enclosure['url']

        # !!!!! MAKE SURE THE DATE IS CONVERTED TO UTC !!!!!
        # !!!!! MAKE SURE IT USES FORMAT: %Y-%m-%d %H:%M:%S !!!!!
        published_at = article.pubDate.get_text(strip=True)  # parse to db date time
        str_time = published_at.split(',')[1].split('+')[0]
        str_time = list(filter(None, str_time.split(' ')))
        str_time[1] = strptime(str_time[1], '%b').tm_mon
        time_from_date = str_time.pop()
        date = "-".join(str(v) for v in str_time[::-1])
        # Convert to UTC (!!! WHEN IT'S NOT DEFINED AS UTC !!!)
        final_date = datetime.strptime(date + " " + time_from_date, "%Y-%m-%d %H:%M:%S")
        local_dt = self.timezone.localize(final_date, is_dst=None)
        published_at = local_dt.astimezone(time_utc).strftime('%Y-%m-%d %H:%M:%S')

        # Visit each article to get data from
        article_link_soup = self.news_page.get_url_content(url)

        author = ""
        author_txt = article.find('dc:creator')
        if author_txt:
            author = author_txt.get_text(strip=True)

        article_content = self.parse_text_content(article_link_soup)

        self.news_page.add_new_article(
            title.strip(), article_content.strip(), url, published_at=published_at, headline=description,
            image_url=url_to_image, author=author, language=language, category=category
        )

    # Logic for class.
    def parse_news(self):
        self.news_page.visit_main_url(parse_type='xml')
        new_urls = []

        # Get all urls from page
        for article in self.news_page.soup.find_all('item'):
            new_urls.append(article)

        # Go through all urls and parse them
        for article in new_urls:
            self.parse_article_data(article)

        print(f"There are {len(self.news_page.new_articles)} articles parsed.")
        self.news_page.store_xls(__file__)


app = RacunalniskeNovice()

try:
    if app.news_page.custom_url is not None:
        content = app.parse_text_content(None, app.news_page.custom_url)
        app.news_page.update_existing_article(content)
    else:
        app.parse_news()
except Exception as e:
    print(e)
