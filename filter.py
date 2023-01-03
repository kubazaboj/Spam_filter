from trainingcorpus import TrainingCorpus
from corpus import Corpus
from bayes import Bayes
from bayes import Bayes_old
from quality import compute_quality_for_corpus
import utils


class MyFilter:
    def __init__(self):
        self.train_dir = {}
        self.spams = []
        self.hams = []
        self.bayes = Bayes()

    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)
        self.bayes.clean_dictionaries()

    def test(self, test_corpus_dir):
        corpus = Corpus(test_corpus_dir)
        results = []
        for file_name, mail in corpus.emails():
            ham_perc = self.evaluate_mail(mail)
            if ham_perc > 0.5:
                results.append((file_name, "OK"))
            else:
                results.append((file_name, "SPAM"))
        self.write_to_file(results, test_corpus_dir)
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

    def write_to_file(self, results, test_corpus_dir):
        with open(test_corpus_dir + "/!prediction.txt", "w") as f:
            for file_name, spam_ham in results:
                f.write(file_name + " " + spam_ham + "\n")


    #removes not intresting parts of texts and converts it to list without duplicates
    def get_list_from_txt(self, text):
        text = utils.skin_text(text)
        text_list = text.split()
        text_list = utils.remove_long(text_list, 20)
        text_list = utils.remove_duplicates(text_list)
        return text_list


if __name__ == "__main__":
    train_dir = "2"
    test_dir = "1"
    myFilter = MyFilter()
    myFilter.train(train_dir)
    print("train spam:", myFilter.bayes.spam_emails_count)
    print("train ham:", myFilter.bayes.ham_emails_count)
    results = myFilter.test(test_dir)
    print("spam:", len([i for i in results if i[1] == "SPAM"]))
    print("ham:", len([i for i in results if i[1] == "OK"]))
    print("quality", compute_quality_for_corpus(test_dir))
