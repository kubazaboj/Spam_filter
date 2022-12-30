from trainingcorpus import TrainingCorpus
import utils as ut


class MyFilter:
    def __init__(self):
        self.train_dir = {}
        self.spams = []
        self.hams = []

    def train(self, train_corpus_dir):
        self.train_dir = self.get_train_dir(train_corpus_dir)
        self.spams = [i for i in list(self.train_dir.keys()) if self.train_dir[i] == "SPAM"]
        self.hams = [i for i in list(self.train_dir.keys()) if self.train_dir[i] == "OK"]

    def test(self, test_corpus_dir):
        pass

    def evaluate_mail(self, email):
        pass

    # creates training dictionary with email derivates(utils)
    @staticmethod
    def get_train_dir(train_corpus_dir):
        t_corpus = TrainingCorpus(train_corpus_dir)
        train_dir = ut.read_classification_from_file(t_corpus.get_train_file_name())
        keys = list(train_dir.keys())
        for key in keys:
            email_derivs = ut.get_email_derivatives(key)
            for deriv in email_derivs:
                train_dir[deriv] = train_dir[key]
        return train_dir


if __name__ == "__main__":
    myFilter = MyFilter()
    myFilter.train("train_dir")
    print("train", myFilter.train_dir)
    print("spams", myFilter.spams)
    print("hams", myFilter.hams)
