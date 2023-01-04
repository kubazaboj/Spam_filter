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
        self.ham_tag = "OK"
        self.spam_tag = "SPAM"
        self.bayes = Bayes()
        self.mails_blacklist = set()
        self.links_blacklist = set()
        self.max_caps_chars_avgs = {'@': 0, '$': 0, '!': 0, 'Caps': 0}

    def train(self, train_corpus_dir):
        self.init_bayes(train_corpus_dir)
        self.bayes.clean_dictionaries()
        self.bayes.calculate_parameters()

    def test(self, test_corpus_dir):
        corpus = Corpus(test_corpus_dir)
        results = []
        for file_name, email in corpus.emails():
            results.append((file_name, self.evaluate_mail(email, file_name)))
        self.write_to_file(results, test_corpus_dir)
        return results

    def evaluate_mail(self, email, filename):
        if self.find_mail_address(email) in self.mails_blacklist:
            return self.spam_tag
        if self.find_link(email) in self.links_blacklist:
            return self.spam_tag
        text_list = self.get_list_from_txt(email)
        spam_perc, ham_perc = self.bayes.evaluate_message(text_list)
        if spam_perc > ham_perc:
            return self.spam_tag
        counter = Pattern_counter()
        for word in email.split():
            if len(word) >= 25 and (word.isnumeric() or word.isalpha()):
                return self.spam_tag
            counter.add_word(word)
        email_caps_char_avgs = counter.calculate_percentages()
        for char in email_caps_char_avgs.keys():
            if email_caps_char_avgs[char] > (self.max_caps_chars_avgs[char]) * 0.5:
                return self.spam_tag
        return self.ham_tag

    def train_blacklist_sender(self, mail):
        for line in mail.split("\n"):
            words = line.split()
            if len(words) > 0:
                if words[0] == "From:":
                    mail = self.isolate_mail(words)
                    self.mails_blacklist.add(mail)

    def find_mail_address(self, mail):
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
    
    def train_spam_links(self, mail):
        for line in mail.split("\n"):
                link_start = "http://"
                if link_start in line:
                    link = self.isolate_link(line.split())
                    if link != "":
                        self.links_blacklist.add(link)


    def find_link(self, mail):
        link = ""
        for line in mail.split("\n"):
            words = line.split()
            if len(words) > 0:
                if "http://" in words:
                    link = self.isolate_link(words)
        return link

    def isolate_link(self, words):
        link = ""
        for word in words:
            if "http://" in word:
                if len(word.split("http://")) != 1:
                    word = word.split("http://")[1]
                else:
                    word = word.split("http://")[0]
                for char in word:
                    if char == "/":
                        break
                    link += char
        if len(link) > 0:
            if link[0].isnumeric():
                return ""
        return link
    

    def init_bayes(self, train_corpus_dir):
        train_corpus = TrainingCorpus(train_corpus_dir)
        for spam_ham, train_mail in train_corpus.train_mails():
            if spam_ham == "SPAM":
                self.train_blacklist_sender(train_mail)
                self.train_spam_links(train_mail)
                
            self.train_caps_chars(train_mail)
            self.bayes.add_spam_ham_count(spam_ham)
            text = self.get_list_from_txt(train_mail)
            for word in text:
                self.bayes.add_word(word, spam_ham)

    def train_caps_chars(self, train_mail):
        counter = Pattern_counter()
        for word in train_mail.split():
            counter.add_word(word)
        caps_chars_avgs = counter.calculate_percentages()
        for char in caps_chars_avgs.keys():
            if caps_chars_avgs[char] > self.max_caps_chars_avgs[char]:
                self.max_caps_chars_avgs[char] = caps_chars_avgs[char]

    def write_to_file(self, results, test_corpus_dir):
        with open(test_corpus_dir + '/!prediction.txt', "w", encoding='utf-8') as f:
            for file_name, spam_ham in results:
                f.write(file_name + " " + spam_ham + "\n")

    # removes not interesting parts of texts and converts it to list without duplicates

    def get_list_from_txt(self, text):
        text = utils.skin_text(text)
        text_list = text.split()
        text_list = utils.remove_long(text_list, 20)
        text_list = utils.remove_duplicates(text_list)
        return text_list

    def check_caps_line(self, line):
        if len(line.split()) == 0:
            return False
        for word in line.split():
            if not word.isupper() or len(word) > 20:
                    return False
        if len(line.split()) < 3:
            return False
        return True


if __name__ == "__main__":
    train_dir = "1"
    test_dir = "2"
    myFilter = MyFilter()
    myFilter.train(train_dir)
    results2 = myFilter.test(test_dir)
    print("spam:", len([i for i in results2 if i[1] == "SPAM"]))
    print("ham:", len([i for i in results2 if i[1] == "OK"]))
    print("quality", compute_quality_for_corpus(test_dir))
    print("caps cahrs avg:", myFilter.max_caps_chars_avgs)
    #print("links blacklist:", myFilter.links_blacklist)
    print("spam dict len:", len(myFilter.bayes.spam_words_counter.keys()))
    print("ham dict len:", len(myFilter.bayes.ham_words_counter.keys()))
