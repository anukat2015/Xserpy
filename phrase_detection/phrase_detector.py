"""Create examples for phrase detection training, train a model, evaluate it on a testing split"""
import argparse, pickle, random,os
from collections import defaultdict

def compute_score(features, weights, index):
    """Compute score a sample has for certain class

    Keyword arguments:
    features -- feature vector of a sample (list of strings)
    weights -- trained model
    index -- desired class

    """
    score = 0
    for feat in features:
        if feat not in weights:
            continue
        score += weights[feat][index]
    return score

def predict(weights, features, cl):
    """Predict best class for a sample

    Keyword arguments:
    weights -- trained model
    features -- feature vector of a sample (list of strings)
    cl -- number of classes

    """
    classes = range(cl)
    scores = defaultdict(float)
    for feat in features:
        if feat not in weights:
            continue
        weight = weights[feat]
        for c,  w in weight.items():
            scores[c] += w
    return max(classes,  key=lambda c: (scores[c],  c))

def init_weights(examples, weights, cl):
    """Initialize or update weights for training

    examples -- set of samples whose features are loaded to weights
    weights -- empty for initializing or partially filled for updating
    cl -- number of classes

    """
    for e, t in examples:
        for f in e:
            if f not in weights.keys():
                weights[f] = {}
                for j in range(cl):
                    weights[f][j] = 0
    return weights

def train(n_iter,  examples, weights, cl, learning_rate):
    """Train a model using perceptron algorithm

    Keyword arguments:
    n_iter -- number of iterations to be used
    examples -- set of training samples in (feature vector, label) shape
    weights -- empty weights
    cl -- number of classes
    learning_rate -- value by which the weights should be changed

    """
    for i in range(n_iter):
        err = 0
        for features,  true in examples:
            guess = predict(weights, features, cl)
            if guess != true:
                for f in features:
                    weights[f][true] += learning_rate
                    weights[f][guess] -= learning_rate
                err += 1.0
        random.shuffle(examples)
        print err/len(examples)
    return weights

def compute_error(features, labels, weights, phrases):
    """Compute accuracy of trained model on an evaluation set

    Keyword arguments:
    features -- feature vectors of samples in testing set
    labels -- gold standard labels of samples in testing set
    weights -- trained model
    phrases -- gold standard labels of samples in testing set, divided according to words in questions

    """
    error = 0
    guesses = []
    for i in range(len(features)):
        label = labels[i]
        guess = predict(weights, features[i],5)
        guesses.append(guess)
        if guess != label:
            error += 1.0
    j = 0
    i = 0
    tot_error = 0
    while j < len(guesses):
        phrase = phrases[i]
        guessed = guesses[j:j+len(phrase)]
        if guessed != phrase:
            tot_error += 1.0
        j += len(phrase)
        i += 1
    print 1.0 - error/len(features)
    print 1.0 - tot_error/len(phrases)

if __name__ == "__main__":
    sep = os.path.sep

    parser = argparse.ArgumentParser(description="Train weights for detecting phrases")
    parser.add_argument("fpath", help="Path to features and labels (array format)", type=str)
    parser.add_argument("n_iter", help="Number of iterations for training", type=int, default=100)
    parser.add_argument("--size", help="Size of dataset", type=int, default=641)
    parser.add_argument("type", help="How examples are loaded", type=str)
    parser.add_argument("mode", help="Training or testing mode, required values: trn or tst", type=str)
    parser.add_argument("--rate", help="Learning rate", type=int, default=1)
    args = parser.parse_args()

    path = args.fpath
    mode = args.mode
    learning_rate = args.rate

    # Mode for creating samples
    if 'l' in args.type:
        words = pickle.load(open(path + "data" + sep + "phrase_detect_features_" + mode + "_" + str(args.size) + "_arr.pickle"))
        labels = pickle.load(open(path + "data" + sep + "labels_" + mode + "_" + str(args.size) + ".pickle"))
        examples = zip(words, labels)
        empty_weights = init_weights(examples, {}, 5)
        pickle.dump(examples, open(path + "data" + sep + "phr_detect_examples_" + mode + "_" + str(args.size) + ".pickle","wb"))
        pickle.dump(empty_weights, open(path + "data" + sep + "empty_weights_" + mode + "_" + str(args.size) + ".pickle","wb"))

    # Mode for computing error
    elif 'e' in args.type:
        features = pickle.load(open(path + "data" + sep + "phrase_detect_features_tst_276_arr.pickle"))
        weights = pickle.load(open(path + "models" + sep + "w_641_i" + str(args.n_iter) + ".pickle"))
        labels = pickle.load(open(path + "data" + sep + "labels_tst_276.pickle"))
        phrases = pickle.load(open(path + "data" + sep + "questions_tst_276.pickle"))
        compute_error(features, labels, weights, phrases)

    # Mode for training model
    else:
        examples = pickle.load(open(path + "data" + sep + "phr_detect_examples_" + mode + "_" + str(args.size) + ".pickle"))
        weights = pickle.load(open(path + "data" + sep + "empty_weights_" + mode + "_" + str(args.size) + ".pickle"))
        w = train(args.n_iter, examples, weights, 5, learning_rate)
        pickle.dump(w, open(path + "models" + sep + "w_" + str(args.size) + "_i" + str(args.n_iter) + ".pickle", "wb"))