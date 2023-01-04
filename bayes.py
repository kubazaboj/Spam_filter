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
        # Function calculating parameters based on their appearance in
        # ham and spam training messages
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

    # Function evaluating the messages based on words in it
    # and their parameters

    def evaluate_message(self, words_list):
        p_spam_given_mess = self.pct_spam
        p_ham_given_mess = self.pct_ham
        for word in words_list:
            multip = False
            multiplier = 1
            if word in self.parameters_spam.keys():
                p_spam_given_mess *= self.parameters_spam[word]
                multiplier = self.parameters_spam[word]
                multip = True
            if word in self.parameters_ham.keys():
                p_ham_given_mess *= self.parameters_ham[word]
                multiplier = self.parameters_ham[word]
                multip = True
            if multip:
                p_spam_given_mess *= 1 / multiplier
                p_ham_given_mess *= 1 / multiplier
        return p_spam_given_mess, p_ham_given_mess

    def clean_dictionaries(self):
        # minimal count of words allowed is spam or ham dictionary
        min_dict_len = 1000
        # remove any words with less than min_num occurences in dictionaries
        min_num = 3
        spam_keys = list(self.spam_words_counter.keys())
        for key in spam_keys:
            if self.spam_words_counter[key] < min_num and len(self.spam_words_counter.keys()) > min_dict_len:
                self.pop_key_spam(key)
        ham_keys = list(self.ham_words_counter.keys())
        for key in ham_keys:
            if self.ham_words_counter[key] < min_num and len(self.ham_words_counter.keys()) > min_dict_len:
                self.pop_key_ham(key)

        # remove words that appear in both spam and ham_filter
        # min_dif_mult = how many times bigger chance must probability be to take as substantial evidence
        min_dif_mult = 4
        spam_keys = list(self.spam_words_counter.keys())
        for key in spam_keys:
            spam_len_ok = len(self.spam_words_counter.keys()) > min_dict_len
            ham_len_ok = len(self.ham_words_counter.keys()) > min_dict_len
            if key in self.ham_words_counter.keys() and spam_len_ok and ham_len_ok:
                word_spam_perc = self.spam_words_counter[key]/self.word_count_spam
                word_ham_perc = self.ham_words_counter[key]/self.word_count_ham
                if max(word_spam_perc, word_ham_perc) / min(word_spam_perc, word_ham_perc) < min_dif_mult:
                    self.pop_key_both(key)
                elif word_spam_perc < word_ham_perc:
                    self.pop_key_spam(key)
                else:
                    self.pop_key_ham(key)
        # remove words shorter than min_len from dictionary
        min_len = 4
        spam_keys = list(self.spam_words_counter.keys())
        for key in spam_keys:
            if len(key) < min_len and len(self.spam_words_counter.keys()) > min_dict_len:
                self.pop_key_spam(key)
        ham_keys = list(self.ham_words_counter.keys())
        for key in ham_keys:
            if len(key) < min_len and len(self.ham_words_counter.keys()) > min_dict_len:
                self.pop_key_ham(key)

        # removes words with the least probability from dictionaries
        to_take = -int(len(self.spam_words_counter)/20)
        to_sort = list(self.spam_words_counter.keys())
        probability_bordrer_key = sorted(to_sort, key=lambda item : self.spam_words_counter[item])[to_take]
        min_prob = self.spam_words_counter[probability_bordrer_key] / self.word_count_spam
        spam_keys = list(self.spam_words_counter.keys())

        for key in spam_keys:
            spam_len_ok = len(self.spam_words_counter.keys()) > min_dict_len
            if self.spam_words_counter[key] / self.word_count_spam < min_prob and spam_len_ok:
                self.pop_key_spam(key)
        ham_keys = list(self.ham_words_counter.keys())
        for key in ham_keys:
            ham_len_ok = len(self.ham_words_counter.keys()) > min_dict_len
            if self.ham_words_counter[key] / self.word_count_ham < min_prob  and ham_len_ok:
                self.pop_key_ham(key)

    def pop_key_spam(self, key):
        self.word_count_spam -= self.spam_words_counter[key]
        self.word_count_total -= self.spam_words_counter[key]
        self.spam_words_counter.pop(key)

    def pop_key_ham(self, key):
        self.word_count_ham -= self.ham_words_counter[key]
        self.word_count_total -= self.ham_words_counter[key]
        self.ham_words_counter.pop(key)

    def pop_key_both(self, key):
        self.word_count_ham -= self.ham_words_counter[key]
        self.word_count_spam -= self.spam_words_counter[key]
        self.word_count_total -= self.ham_words_counter[key] + self.spam_words_counter[key]
        self.ham_words_counter.pop(key)
        self.spam_words_counter.pop(key)
