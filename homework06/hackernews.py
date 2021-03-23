from bottle import (
    route, run, template, request, redirect
)

from scrapper import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    query = request.query.decode()
    id = int(query['id'])
    label = query['label']
    s = session()
    s.query(News.id).filter(News.id == id).update({News.label: label})
    s.commit()
    redirect("/news")


def has(ses, author, title):
    return (len(ses.query(News.author).filter_by(author=author).all()) == 0 or
            len(ses.query(News.title).filter_by(title=title).all()) == 0)


@route("/update")
def update_news():
    news = get_news('https://news.ycombinator.com/', 3)
    s = session()
    for n in news:
        if has(s, n['author'], n['title']):
            s.add(News(title=n['title'],
                       author=n['author'],
                       url=n['url'],
                       points=n['points'],
                       comments=n['comments']))
    s.commit()
    redirect("/news")


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


@route("/classify")
def classify_news():
    s = session()
    model = NaiveBayesClassifier()
    train_set = s.query(News).filter(News.label != None).all()
    model.fit([clean(news.title).lower() for news in train_set], [news.label for news in train_set])
    test = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=sorted(
        test,
        key=lambda news: get_weight(model.predict(clean(news.title).lower())))
    )


def get_weight(label):
    if label == 'never':
        return 2
    elif label == 'maybe':
        return 1
    elif label == 'good':
        return 0
    else:
        raise AssertionError("Invalid label" + label)


if __name__ == "__main__":
    run(host="localhost", port=8080)


