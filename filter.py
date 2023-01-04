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
        self.caps_avgs = {}
        self.blacklist = set()

    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)
        self.bayes.clean_dictionaries()
        self.bayes.calculate_parameters()

    def test(self, test_corpus_dir):
        corpus = Corpus(test_corpus_dir)
        results = []
        for file_name, mail in corpus.emails():
            if self.find_email_address(mail) in self.blacklist:
                results.append((file_name, "SPAM"))
                continue
            spam_perc, ham_perc, caps_avg = self.evaulate_mail(mail)
            if spam_perc > ham_perc or caps_avg > 0.1:
                results.append((file_name, "SPAM"))
            else:
                results.append((file_name, "OK"))
            #print(spam_perc, ham_perc, results[-1][1])
        self.write_to_file(results, test_corpus_dir)
        return results

    def evaulate_mail(self, email):
        # capslock bonus
        counter = Pattern_counter()
        for word in email.split():
            counter.add_word(word)
        caps_avg = counter.caps_count / counter.word_count
        #bayes
        text_list = self.get_list_from_txt(email)
        spam, ham = self.bayes.evaluate_message(text_list)
        return spam, ham, caps_avg

    def train_balcklist(self, mail):
        for line in mail.split("\n"):
            words = line.split()
            if len(words) > 0:
                if words[0] == "From:":
                    mail = self.isolate_mail(words)
                    self.blacklist.add(mail)

    def find_email_address(self, mail):
        for line in mail.split("\n"):
            words = line.split()
            if len(words) > 0:
                if words[0] == "From:":
                    mail = self.isolate_mail(words)
                    return mail

    def isolate_mail(self, words):
        mail = ""
        for word in words:
            if "@" in word:
                for char in word:
                    if char.isnumeric() or char.isalpha() or char == "@":
                        mail += char
                break
        return mail

    def init_bayes(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        self.caps_avgs = {"SPAM": 0, "OK": 0, "ALL": 0}
        mail_counts = {"SPAM": 0, "OK": 0, "ALL": 0}
        for spam_ham, train_mail in train_corpus.train_mails():
            if spam_ham == "SPAM":
                self.train_balcklist(train_mail)
            self.train_caps(train_mail, spam_ham, mail_counts)
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)
        self.caps_avgs["SPAM"] = self.caps_avgs["SPAM"] / mail_counts["SPAM"]
        self.caps_avgs["OK"] = self.caps_avgs["OK"] / mail_counts["OK"]
        self.caps_avgs["ALL"] = self.caps_avgs["ALL"] / mail_counts["ALL"]


    def train_caps(self, train_mail, spam_ham, mail_counts):
        counter = Pattern_counter()
        if spam_ham == "SPAM":
            mail_counts["SPAM"] += 1
            mail_counts["ALL"] += 1
            for word in train_mail.split():
                counter.add_word(word)
            self.caps_avgs["SPAM"] += counter.caps_count / counter.word_count
            self.caps_avgs["ALL"] += counter.caps_count / counter.word_count
        if spam_ham == "OK":
            mail_counts["OK"] += 1
            mail_counts["ALL"] += 1
            for word in train_mail.split():
                counter.add_word(word)
            self.caps_avgs["OK"] += counter.caps_count / counter.word_count
            self.caps_avgs["ALL"] += counter.caps_count / counter.word_count

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
    train_dir = "1"
    test_dir = "2"
    myFilter = MyFilter()
    t0 = time.time_ns()
    myFilter.train(train_dir)
    print("train time:", (time.time_ns() - t0) / 1e6, "ms")
    results2 = myFilter.test(test_dir)
    print("spam:", len([i for i in results2 if i[1] == "SPAM"]))
    print("ham:", len([i for i in results2 if i[1] == "OK"]))
    print("quality", compute_quality_for_corpus(test_dir))
    print("caps avg:", myFilter.caps_avgs)
    print("spam dict len:", len(myFilter.bayes.spam_words_counter.keys()))
    print("ham dict len:", len(myFilter.bayes.ham_words_counter.keys()))
