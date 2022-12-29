import os
from utils import read_classification_from_file


class Corpus:
    def __init__(self, dirname):
        self.dirname = dirname

    def emails(self):
        files = [x for x in os.listdir(self.dirname) if x[0] != "!"]
        for file in files:
            with open(self.dirname + "/" + file, encoding='utf-8') as f:
                yield file, f.read()

    def results(self):
        files = ["!truth.txt", "!prediction.txt"]
        return read_classification_from_file(self.dirname + "/" + files[0]) \
            , read_classification_from_file(self.dirname + "/" + files[1])


if __name__ == "__main__":
    corpus = Corpus("emails")
    for i, j in corpus.emails():
        print(i)
        print(j)
        print("------------------------")
