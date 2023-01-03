from corpus import Corpus
import utils


class TrainingCorpus(Corpus):

    def train_mails(self):
        file = "!truth.txt"
        truth_dir = utils.read_classification_from_file(self.dirname + "/" + file)
        for name, mail in self.emails():
            spam_ham = truth_dir[name]
            yield spam_ham, mail

    def get_train_file_name(self):
        return self.dirname + "/" + "!truth.txt"
