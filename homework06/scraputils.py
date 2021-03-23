import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """ Extract news from a given web page """

    def extract_first_integer_from_tag(tag, separator):
        try:
            return 0 if tag is None else int(tag.text.split(separator)[0])
        except ValueError:
            return 0

    news_list = []

    news = parser.findAll("a", {"class": "storylink"})
    subtexts = parser.findAll("td", {"class": "subtext"})

    for new in range(len(news)):
        author = subtexts[new].find("a", {"class": "hnuser"})
        comments = extract_first_integer_from_tag(subtexts[new].find_all("a")[-1], "\xa0")
        points = extract_first_integer_from_tag(subtexts[new].find("span", {"class": "score"}), " ")

        news.append(
            {
                "author": None if author is None else author.text,
                "comments": comments,
                "points": points,
                "title": news[new].text,
                "url": news[new]["href"],
            }
        )

    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    return parser.find("a", {"class": "morelink"})["href"]


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
