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
        self.max_caps_chars_avgs = {}

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
            spam_perc, ham_perc = self.evaulate_mail(mail)
            if spam_perc > ham_perc:
                results.append((file_name, "SPAM"))
            else:
                counter = Pattern_counter()
                for word in mail.split():
                    counter.add_word(word)
                email_caps_char_avgs = counter.calculate_percentages()
                result_eval = False
                for char in email_caps_char_avgs.keys():
                    if email_caps_char_avgs[char] > (self.max_caps_chars_avgs[char]) * 0.5:
                        print("XD")
                        results.append((file_name, "SPAM"))
                        result_eval = True
                        break
                if result_eval:
                    continue
                results.append((file_name, "OK"))
            #print(spam_perc, ham_perc, results[-1][1])
        self.write_to_file(results, test_corpus_dir)
        return results

    def evaulate_mail(self, email):
        #bayes
        text_list = self.get_list_from_txt(email)
        spam, ham = self.bayes.evaluate_message(text_list)
        return spam, ham

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
        self.max_caps_chars_avgs = {'@': 0, '$': 0, '!': 0, 'Caps': 0}
        mail_counts = {"SPAM": 0, "OK": 0, "ALL": 0}
        for spam_ham, train_mail in train_corpus.train_mails():
            if spam_ham == "SPAM":
                self.train_balcklist(train_mail)
            self.train_caps_chars(train_mail, spam_ham, mail_counts)
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)


    def train_caps_chars(self, train_mail, spam_ham, mail_counts):
        counter = Pattern_counter()
        for word in train_mail.split():
            counter.add_word(word)
        
        caps_chars_avgs = counter.calculate_percentages()
        #print("maximal caps and chars average", self.max_caps_chars_avgs)
        for char in caps_chars_avgs.keys():
            if caps_chars_avgs[char] > self.max_caps_chars_avgs[char]:
                self.max_caps_chars_avgs[char] = caps_chars_avgs[char]

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
    print("caps cahrs avg:", myFilter.max_caps_chars_avgs)
    print("spam dict len:", len(myFilter.bayes.spam_words_counter.keys()))
    print("ham dict len:", len(myFilter.bayes.ham_words_counter.keys()))
