import pickle
from collections import defaultdict


class AveragedPerceptron(object):

    def __init__(self, classes=None, lr=1.0):
        super().__init__()
        # weights a dict of dict, weights[feature][class] = float
        self.weights = defaultdict(lambda: defaultdict(float))
        # Set of all the possible tags
        self.classes = set()
        if classes is not None:
            self.classes = set(classes)
        # Accumulated weight values implemented as
        # _weight_totals[feature][class] = float
        self._weight_totals = defaultdict(lambda: defaultdict(float))
        # When was the last time this weight was updated
        # _weights_tstamps[feature][class] = int
        self._weight_tstamps = defaultdict(lambda: defaultdict(int))
        self.i = 0
        self.lr = lr

    def dot(self, features):
        """Dot product the feature vector with each weight vector."""
        # Get the score for each class
        scores = defaultdict(float)
        # Iterate over all the features
        for feat, value in features.items():
            if feat not in self.weights or value == 0:
                continue
            # Look up the weights associated with that feature
            # dict of weights[class] = weight
            weights = self.weights[feat]
            for label, weight in weights.items():
                # for each class multiply feature * weight
                # for this feature, class
                scores[label] += value * weight
        return scores

    def predict(self, features):
        scores = self.dot(features)
        # get the class with the max score
        return max(self.classes, key=lambda label: (scores[label], label))

    def update(self, truth, guess, features):
        def update_features(c, f, w, lr, v):
            self._update_accumulator(f, c, w)
            # Update the weight
            self.weights[f][c] = w + (lr * v)

        self.i += 1
        # if we were were right don't change anything
        if truth == guess:
            return
        # Update all the feature weights for the correct class and predicted class.
        for f, w in features.items():
            weights = self.weights[f]
            update_features(truth, f, weights[truth], self.lr, w)
            update_features(guess, f, weights[guess], self.lr, -w)

    def _update_accumulator(self, feature, class_, weight):
        # Use the timestamp to update the accumulator
        self._weight_totals[feature][class_] += (self.i - self._weight_tstamps[feature][class_]) * weight
        self._weight_tstamps[feature][class_] = self.i

    def average_weights(self):
        for feat, weights in self.weights.items():
            new_feat_weights = defaultdict(int)
            for clas, weight in weights.items():
                self._update_accumulator(feat, clas, weight)
                total = self._weight_totals[feat][clas]
                averaged = round(total / self.i, 3)
                if averaged:
                    new_feat_weights[clas] = averaged
            self.weights[feat] = new_feat_weights

    def save(self, path):
        pickle.dump([dict(self.weights), self.classes], open(path, 'wb'))

    @classmethod
    def load(cls, path):
        model = cls()
        model.weights, model.classes = pickle.load(open(path, "rb"))
        return model
