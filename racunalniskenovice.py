from datetime import datetime
from pytz import timezone, utc as time_utc
from time import strptime
from newspage import NewsPage


class RacunalniskeNovice:
    news_page = None
    timezone = timezone("Europe/Ljubljana")

    def __init__(self):
        self.news_page = NewsPage()
        self.news_page.url = 'https://racunalniske-novice.com/feed/'

    def parse_news(self):
        self.news_page.visit_main_url(parse_type='xml')
        language = "slovenščina"
        new_urls = []

        for article in self.news_page.soup.find_all('item'):
            new_urls.append(article)

        for article in new_urls:
            url = article.link.get_text()
            title = article.title.get_text(strip=True)
            category = ""
            categories = article.findAll('category')
            for c in categories:
                category += c.get_text(strip=True) + " / "

            category = category[:-2]
            url_to_image = article.enclosure['url']

            published_at = article.pubDate.get_text(strip=True)  # parse to db date time
            str_time = published_at.split(',')[1].split('+')[0]
            str_time = list(filter(None, str_time.split(' ')))
            str_time[1] = strptime(str_time[1], '%b').tm_mon
            time_from_date = str_time.pop()
            date = "-".join(str(v) for v in str_time[::-1])
            # Convert to UTC
            final_date = datetime.strptime(date + " " + time_from_date, "%Y-%m-%d %H:%M:%S")
            local_dt = self.timezone.localize(final_date, is_dst=None)
            published_at = local_dt.astimezone(time_utc).strftime('%Y-%m-%d %H:%M:%S')

            # Visit each article to get data from
            article_link_soup = self.news_page.get_url_content(url)

            author = ""
            author_txt = article.find('dc:creator')
            if author_txt is not None:
                author = author_txt.get_text(strip=True)

            content = ""
            if article_link_soup is not None:
                content_soap = article_link_soup.find('div', class_='summary')
                content = content_soap.get_text() + " "
                content_soap_two = article_link_soup.find('div', class_='content')
                if content_soap_two is not None:
                    for p in content_soap_two.find_all('p'):
                        content += p.get_text() + " "

            self.news_page.add_article(
                title.strip(), content.strip(), url, published_at=published_at,
                image_url=url_to_image, author=author, language=language, category=category
            )

        print(f"There are {len(self.news_page.new_articles)} articles parsed.")


app = RacunalniskeNovice()

try:
    app.parse_news()
except Exception as e:
    print(e)
