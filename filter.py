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
        self.spam_pattern_counter = Pattern_counter()
        self.ham_pattern_counter = Pattern_counter()
        self.pattern_threshold = 0.01
        self.importance_jump = 1.05


    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)
        self.bayes.clean_dictionaries()
        self.bayes.calculate_parameters()
        self.train_patterns(train_corpus_dir)

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
        text_list = self.get_list_from_txt(email)
        spam, ham = self.bayes.evaluate_message(text_list)
        #evaluate with patterns
        new_counter = Pattern_counter()
        for word in email.split():
            new_counter.add_word(word)
        new_counter.calculate_percentages()
        for pattern in new_counter.percentages.keys():
            if not pattern in list(self.spam_pattern_counter.percentages.keys()) + list(self.ham_pattern_counter.percentages.keys()):
                continue
            spam_perc = self.spam_pattern_counter.percentages[pattern]
            if abs(new_counter.percentages[pattern] - spam_perc) < self.pattern_threshold * spam_perc:
                spam *= self.spam_pattern_counter.importance[pattern]
            ham_perc = self.ham_pattern_counter.percentages[pattern]
            if abs(new_counter.percentages[pattern] - ham_perc) < self.pattern_threshold * ham_perc:
                ham *= self.ham_pattern_counter.importance[pattern]
        return spam, ham

    def init_bayes(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        for spam_ham, train_mail in train_corpus.train_mails():
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)
            for word in train_mail.split():
                self.add_to_pattern_counters(word, spam_ham)
        self.spam_pattern_counter.calculate_percentages()
        self.ham_pattern_counter.calculate_percentages()

    def add_to_pattern_counters(self, word, spam_ham):
        if spam_ham == "SPAM":
            self.spam_pattern_counter.add_word(word)
        else:
            self.ham_pattern_counter.add_word(word)

    def train_patterns(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        for spam_ham, train_mail in train_corpus.train_mails():
            new_counter = Pattern_counter()
            for word in train_mail.split():
                new_counter.add_word(word)
            new_counter.calculate_percentages()
            print(new_counter)
            # check if any patterns are close to spam_pattern_counter
            if spam_ham == "SPAM":
                for pattern in new_counter.percentages.keys():
                    spam_perc = self.spam_pattern_counter.percentages[pattern]
                    if abs(new_counter.percentages[pattern] - spam_perc) < self.pattern_threshold * spam_perc:
                        self.spam_pattern_counter.importance[pattern] *= self.importance_jump
                        self.ham_pattern_counter.importance[pattern] /= self.importance_jump
            # check if any patterns are close to ham_pattern_counter
            else:
                for pattern in new_counter.percentages.keys():
                    ham_perc = self.ham_pattern_counter.percentages[pattern]
                    if abs(new_counter.percentages[pattern] - ham_perc) < self.pattern_threshold * ham_perc:
                        self.spam_pattern_counter.importance[pattern] /= self.importance_jump
                        self.ham_pattern_counter.importance[pattern] *= self.importance_jump

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
    print("spam importance:", myFilter.spam_pattern_counter.importance)
    print("ham importance:", myFilter.ham_pattern_counter.importance)
