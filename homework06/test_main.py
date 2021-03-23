import bayes
import csv
import hackernews
import scraputils
import requests
from bs4 import BeautifulSoup


def test_clear():
    assert hackernews.clean("A") == "A"
    assert hackernews.clean("A, B, C") == "A B C"
    assert hackernews.clean("A.a()") == "Aa"


def test_classification_single_words():
    x_train = [hackernews.clean(s).lower() for s in "The quick brown fox jumps over the lazy dog".split()]
    y_train = ["NOT_ANIMAL"] * 3 + ["ANIMAL"] + ["NOT_ANIMAL"] * 4 + ["ANIMAL"]

    model = bayes.NaiveBayesClassifier()
    model.fit(x_train, y_train)

    assert model.score(x_train, y_train) == 1


def test_classification_massages_dataset():
    with open("data/SMSSpamCollection") as file:
        dataset = list(csv.reader(file, delimiter="\t"))
    msgs, targets = [], []
    for target, msg in dataset:
        msgs.append(msg)
        targets.append(target)

    msgs = [hackernews.clean(msg).lower() for msg in msgs]
    msgs_train, targets_train, msgs_test, targets_test = msgs[:3900], targets[:3900], msgs[3900:], targets[3900:]

    model = bayes.NaiveBayesClassifier()
    model.fit(msgs_train, targets_train)

    assert model.score(msgs_test, targets_test) > 0.95


def test_next_page_parser():
    url = "https://news.ycombinator.com/"
    for i in range(2, 5):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        next_url = scraputils.extract_next_page(soup)
        assert next_url == "news?p=" + str(i)
        url = "https://news.ycombinator.com/" + next_url
