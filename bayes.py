SMOOTH_PAR = 1  # Smoothing parametr for calcuclating the probability of ham/spam

class Bayes:
    def __init__(self):
        self.spam_words_counter = {}
        self.ham_words_counter = {}
        self.spam_emails_count = 0
        self.ham_emails_count = 0
        self.total_email_count = 0
        self.pct_spam = 0
        self.pct_ham = 0
        self.word_count_ham = 0
        self.word_count_spam = 0
        self.word_count_total = 0
        self.parameters_ham = {}
        self.parameters_spam = {}
        self.spam = "SPAM"
        self.ham = "OK"

        # call this when training on new mail

    def add_spam_ham_count(self, email_label):
        self.total_email_count += 1
        if email_label == self.spam:
            self.spam_emails_count += 1
            self.pct_spam = self.spam_emails_count / self.total_email_count
        else:
            self.ham_emails_count += 1
            self.pct_ham = self.ham_emails_count / self.total_email_count

        # call this on every word from mail

    def add_word(self, word, email_label):
        self.word_count_total += 1
        if email_label == self.spam:
            self.add_to_dict(self.spam_words_counter, word)
            self.word_count_spam += 1
        else:
            self.add_to_dict(self.ham_words_counter, word)
            self.word_count_ham += 1

        # ads count of given word, if word is not in dictionary it adds it there

    def add_to_dict(self, dict, key):
        try:
            dict[key] += 1
        except KeyError:
            dict[key] = 1

    def combine_dictionaries(self, dict1, dict2):
        new_dict = {}
        for key in dict1.keys():
            new_dict[key] = dict1[key]
        for key in dict2.keys():
            try:
                new_dict[key] += dict2[key]
            except KeyError:
                new_dict[key] = dict2
        return new_dict

    def try_get_from_dict(self, dict1, key):
        try:
            return dict1[key]
        except KeyError:
            return 0

    def calculate_parameters(self):
        #Function calculating parameters based on their appearance in 
        #ham and spam training messages
        all_words_counter = self.combine_dictionaries(self.spam_words_counter, self.ham_words_counter)
        self.parameters_ham = {word: 0 for word in list(all_words_counter.keys())}
        self.parameters_spam = {word: 0 for word in list(all_words_counter.keys())}
        for word in all_words_counter.keys():
            n_word_spam = self.try_get_from_dict(self.spam_words_counter, word)
            p_word_spam = (n_word_spam + SMOOTH_PAR) / (self.word_count_spam + SMOOTH_PAR * len(all_words_counter.keys()))
            self.parameters_spam[word] = p_word_spam

            n_word_ham = self.try_get_from_dict(self.ham_words_counter, word)
            p_word_ham = (n_word_ham + SMOOTH_PAR) / (self.word_count_ham + SMOOTH_PAR * len(all_words_counter.keys()))
            self.parameters_ham[word] = p_word_ham

    def evaluate_message(self, words_list):
        #Function evaluating the messages based on words in it 
        #and their parameters
        p_spam_given_mess = self.pct_spam
        p_ham_given_mess = self.pct_ham
        for word in words_list:
            if word in self.parameters_spam.keys():
                p_spam_given_mess *= self.parameters_spam[word]
            if word in self.parameters_ham.keys():
                p_ham_given_mess *= self.parameters_ham[word]
        return p_spam_given_mess, p_ham_given_mess

    def clean_dictionaries(self):
        # remove any words with less than min_num occurences
        min_num = 3
        spam_keys = list(self.spam_words_counter.keys())
        for i in spam_keys:
            if self.spam_words_counter[i] < min_num:
                self.word_count_spam -= self.spam_words_counter[i]
                self.word_count_total -= self.spam_words_counter[i]
                self.spam_words_counter.pop(i)
        ham_keys = list(self.ham_words_counter.keys())
        for i in ham_keys:
            if self.ham_words_counter[i] < min_num:
                self.word_count_ham -= self.ham_words_counter[i]
                self.word_count_total -= self.ham_words_counter[i]
                self.ham_words_counter.pop(i)

        # remove words that appear in both spam and ham_filter
        # min_dif_mult = how many times bigger chance must there be to take as substantial evidence
        min_dif_mult = 3
        spam_keys = list(self.spam_words_counter.keys())
        for key in spam_keys:
            if key in self.ham_words_counter.keys():
                word_spam_perc = self.spam_words_counter[key]/self.word_count_spam
                word_ham_perc = self.ham_words_counter[key]/self.word_count_ham
                if max(word_spam_perc, word_ham_perc) / min(word_spam_perc, word_ham_perc) < min_dif_mult:
                    self.word_count_ham -= self.ham_words_counter[key]
                    self.word_count_spam -= self.spam_words_counter[key]
                    self.word_count_total -= self.ham_words_counter[key] + self.spam_words_counter[key]
                    self.ham_words_counter.pop(key)
                    self.spam_words_counter.pop(key)
                elif word_spam_perc < word_ham_perc:
                    self.word_count_spam -= self.spam_words_counter[key]
                    self.word_count_total -= self.spam_words_counter[key]
                    self.spam_words_counter.pop(key)
                else:
                    self.word_count_ham -= self.ham_words_counter[key]
                    self.word_count_total -= self.ham_words_counter[key]
                    self.ham_words_counter.pop(key)
