from collections import defaultdict
from math import log


class NaiveBayesClassifier:
    def __init__(self, a: int = 1e-5):
        self.d = 0
        self.word = defaultdict(lambda: 0)
        self.classified_words = defaultdict(lambda: 0)
        self.classes = defaultdict(lambda: 0)
        self.a = a

    def fit(self, dataset, classes):
        """ Fit Naive Bayes classifier according to titles, labels. """

        for i in range(len(dataset)):
            self.classes[classes[i]] += 1
            words = dataset[i].split()
            for w in words:
                self.word[w] += 1
                self.classified_words[w, classes[i]] += 1

        for c in self.classes:
            self.classes[c] /= len(dataset)

        self.d = len(self.word)

    def predict(self, feature):
        """ Perform classification on an array of test vectors X. """
        assert len(self.classes) > 0
        return max(
            self.classes.keys(),
            key=lambda c: log(self.classes[c])
            + sum(
                log((self.classified_words[w, c] + self.a) / (self.word[w] + self.a * self.d))
                for w in feature.split()
            ),
        )

    def _get_predictions(self, dataset):
        classes = []
        for feature in dataset:
            classes.append(self.predict(feature))
        return classes

    def score(self, dataset, classes):
        """ Returns the mean accuracy on the given test data and labels. """
        predicted = self._get_predictions(dataset)
        return sum(0 if predicted[i] != classes[i] else 1 for i in range(len(dataset))) / len(
            dataset
        )
