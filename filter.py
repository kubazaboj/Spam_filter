from trainingcorpus import TrainingCorpus
from corpus import Corpus
from bayes import Bayes2
import utils


class MyFilter:
    def __init__(self):
        self.train_dir = {}
        self.spams = []
        self.hams = []
        self.bayes = Bayes2()

    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)

    def test(self, test_corpus_dir):
        corpus = Corpus(test_corpus_dir)
        results = []
        for file_name, mail in corpus.emails():
            if self.evaluate_mail(mail) > 0.5:
                results.append("OK")
            else:
                results.append("SPAM")
        return results

    def evaluate_mail(self, email):
        text_list = self.get_list_from_txt(email)
        ham_perc = self.bayes.calculate_ham_chance(text_list)
        return ham_perc

    def init_bayes(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        for spam_ham, train_mail in train_corpus.train_mails():
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)

    #removes not intresting parts of texts and converts it to list without duplicates
    def get_list_from_txt(self, text):
        text = utils.skin_text(text)
        text_list = text.split()
        text_list = utils.remove_duplicates(text_list)
        return text_list


if __name__ == "__main__":
    myFilter = MyFilter()
    myFilter.train("1")
    results = myFilter.test("1")
    print(len([i for i in results if i == "SPAM"]))
    print(len([i for i in results if i == "OK"]))
