import math
from collections import Counter


class NaiveBayesClassifier:
    def __init__(self, alpha: float = 1e-5):
        self.alpha = alpha
        self.model: dict = {
            "labels": {},
            "words": {},
        }

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y."""
        catalog = []
        for title, lable in zip(X, y):
            for word in title.split():
                pair = (word, lable)
                catalog.append(pair)

        self.unique_words = Counter(catalog)
        print("unique_words", self.unique_words)

        self.counted_dict = dict(Counter(y))
        print("counted_dict", self.counted_dict)

        words = [word for title in X for word in title.split()]
        self.counted_words = dict(Counter(words))
        print("counted_words", self.counted_words)

        self.model = {
            "labels": {},
            "words": {},
        }

        for edition in self.counted_dict:
            count = 0
            for word, label_name in self.unique_words:
                if edition == label_name:
                    count += self.unique_words[(word, edition)]
            params = {
                "label_count": count,
                "probability": self.counted_dict[edition] / len(y),
            }
            self.model["labels"][edition] = params

        for word in self.counted_words:
            params = {}
            for edition in self.counted_dict:
                nc = self.model["labels"][edition]["label_count"]
                nic = self.unique_words.get((word, edition), 0)
                counted_len = len(self.counted_words)
                alpha = self.alpha
                smooth = (nic + alpha) / (nc + alpha * counted_len)
                params[edition] = smooth
            self.model["words"][word] = params

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        words = X.split()
        chance = []
        for cur_label in self.model["labels"]:
            probability = self.model["labels"][cur_label]["probability"]
            total_grade = math.log(probability, math.e)
            for word in words:
                word_dict = self.model["words"].get(word, None)
                if word_dict:
                    total_grade += math.log(word_dict[cur_label], math.e)
            chance.append((total_grade, cur_label))
        _, prediction = max(chance)
        return prediction

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        correct = []
        for one in X_test:
            correct.append(self.predict(one))
        return sum(0 if correct[i] != y_test[i] else 1 for i in range(len(X_test))) / len(X_test)
