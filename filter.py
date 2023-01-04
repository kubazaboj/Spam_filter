import time

from trainingcorpus import TrainingCorpus
from corpus import Corpus
from bayes import Bayes
from quality import compute_quality_for_corpus
from pattern_counter import Pattern_counter
import utils


class MyFilter:
    def __init__(self):
        self.train_dir = {}
        self.spams = []
        self.hams = []
        self.bayes = Bayes()
        self.pattern_threshold = 0.01
        self.importance_jump = 1.05
        self.avg_caps = 0
        self.caps_importance = 5


    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)
        self.bayes.clean_dictionaries()
        self.bayes.calculate_parameters()

    def test(self, test_corpus_dir):
        corpus = Corpus(test_corpus_dir)
        results = []
        for file_name, mail in corpus.emails():
            spam_perc, ham_perc = self.evaulate_mail(mail)
            if spam_perc > ham_perc:
                results.append((file_name, "SPAM"))
            else:
                results.append((file_name, "OK"))
        self.write_to_file(results, test_corpus_dir)
        return results

    def evaulate_mail(self, email):
        counter = Pattern_counter()
        for word in email.split():
            counter.add_word(word)
        caps_avg = counter.caps_count / counter.word_count
        spam_boost = (caps_avg / self.avg_caps) * self.caps_importance + 1
        text_list = self.get_list_from_txt(email)
        spam, ham = self.bayes.evaluate_message(text_list)
        return spam * spam_boost, ham

    def init_bayes(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        caps_perc = 0
        mail_count = 0
        for spam_ham, train_mail in train_corpus.train_mails():
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)
            counter = Pattern_counter()
            if spam_ham == "SPAM":
                mail_count += 1
                for word in train_mail.split():
                    counter.add_word(word)
                caps_perc += counter.caps_count/counter.word_count
        self.avg_caps = caps_perc / mail_count


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
    test_dir = "2"
    myFilter = MyFilter()
    t0 = time.time_ns()
    myFilter.train(train_dir)
    print("train time:", (time.time_ns() - t0) / 1e6, "ms")
    results2 = myFilter.test(test_dir)
    print("spam:", len([i for i in results2 if i[1] == "SPAM"]))
    print("ham:", len([i for i in results2 if i[1] == "OK"]))
    print("quality", compute_quality_for_corpus(test_dir))
    print("caps avg:", myFilter.avg_caps)
