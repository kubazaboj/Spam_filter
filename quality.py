from corpus import Corpus
from confmat import BinaryConfusionMatrix

def quality_score(tp, tn, fp, fn):
    return (tp + tn) / (tp + tn + 10*fp + fn)

def compute_quality_for_corpus(corpus_dir):
    corpus = Corpus(corpus_dir)
    truth, predict = corpus.results()
    mat = BinaryConfusionMatrix("SPAM", "OK")
    mat.compute_from_dicts(truth, predict)
    return quality_score(mat.TP, mat.TN, mat.FP, mat.FN)
