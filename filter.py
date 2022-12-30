from trainingcorpus import TrainingCorpus
import utils as ut


class MyFilter:
    def train(self, train_corpus_dir):
        train_dir = self.get_train_dir(train_corpus_dir)


    def test(self, test_corpus_dir):
        pass

    # creates training dictionary with email derivates(utils)
    def get_train_dir(self, train_corpus_dir):
        t_corpus = TrainingCorpus(train_corpus_dir)
        train_dir = ut.read_classification_from_file(t_corpus.get_train_file_name())
        keys = list(train_dir.keys())
        for key in keys:
            email_derivs = ut.get_email_derivatives(key)
            for deriv in email_derivs:
                train_dir[deriv] = train_dir[key]
        return train_dir


if __name__ == "__main__":
    filter = MyFilter()
    filter.train("train_dir")
