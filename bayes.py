SMOOTH_PAR = 1  # Smoothing parametr for calcuclating the probability of ham/spam

"""The old version, just if we need it."""


class Bayes_old:
    def __init__(self, labels_filename):
        self.labels_filename = labels_filename

    def load_emails(self):
        train_emails = {}
        # The dictionary of training emails and their labels
        with open(self.labels_filename, 'r', encoding='utf-8') as labels_file:
            for line in labels_file:
                train_emails[line[0]] = line[1]
            # Opening the prediction to get the dictionary of emails and their label
        return train_emails

    def divide_emails_by_labels(self, train_emails):
        # Dividing messages by their label
        spam_messages = [spam for spam in train_emails.keys() if train_emails[spam] == "SPAM"]
        ham_messages = [ham for ham in train_emails.keys() if train_emails[ham] == "HAM"]
        no_of_emails = len(train_emails)  # Total number of all emails
        pct_spam = len(spam_messages) / no_of_emails  # The percantage of spam emails in the training set
        pct_ham = len(ham_messages) / no_of_emails  # The percantage of ham emails in the training set
        return pct_spam, pct_ham

    def vocab_loading(self, train_emails):
        no_words_spam = 0  # Total number of words in all spam messages
        no_words_ham = 0  # Total number of words in all ham messages
        vocab_spam = {}  # The dictionary consisting of all words used in spam messages
        vocab_ham = {}  # The dictionary consisting of all words used in ham messages
        for email_file in train_emails.keys():
            with open(email_file, 'r', encoding='utf-8') as email:
                # Clean the email from html tags and have only body...
                # Then create a vocabulary dictionary
                for line in email:
                    for word in line:
                        if train_emails[email_file] == "SPAM":
                            no_words_spam += 1
                            if word in vocab_spam.keys():
                                vocab_spam[word] += 1
                            else:
                                vocab_spam[word] = 1
                        else:
                            no_words_ham += 1
                            if word in vocab_ham.keys():
                                vocab_ham[word] += 1
                            else:
                                vocab_ham[word] = 1
        return vocab_spam, vocab_ham, no_words_spam, no_words_ham

    def calc_vocab_len(self, vocab_ham, vocab_spam):
        vocab = {**vocab_ham,
                 **vocab_spam}  # Merging ham and spam words dictionary together to have all words in one dictionary
        vocab_len = len(vocab)  # Total number of words in both, ham and spam words dictionaries
        return vocab_len

    def parameters_cals(self, vocab_ham, vocab_spam, no_words_spam):
        parameters_spam_words = {}  # The dictionary of parameters for all words in spam messages
        parameters_ham_words = {}  # The dictionary of parameters for all words in ham messages
        vocab_len = self.calc_vocab_len(vocab_ham, vocab_spam)
        for word in vocab_ham:
            par_ham_word_given = (vocab_ham[word] + SMOOTH_PAR) / (no_words_spam + SMOOTH_PAR * vocab_len)
            # Counting the parametr value for specified ham word in the dictionary
            parameters_ham_words[word] = par_ham_word_given
            # Adding the parameter to the dictionary of all ham words parameters in the dictionary
        for word in vocab_spam:
            par_spam_word_given = (vocab_ham[word] + SMOOTH_PAR) / (no_words_spam + SMOOTH_PAR * vocab_len)
            # Counting the parametr value for specified spam word in the dictionary
            parameters_spam_words[word] = par_spam_word_given
            # Adding the parameter to the dictionary of all spam words parameters in the dictionary
        return parameters_ham_words, parameters_spam_words


"""The actual Bayes we are using rn"""


class Bayes_new_old:
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

    def try_get_from_dict(self, dict1, key):
        try:
            return dict1[key]
        except KeyError:
            return 0

    def calculate_parameters(self):
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
        p_spam_given_mess = self.pct_spam
        p_ham_given_mess = self.pct_ham
        for word in words_list:
            if word in self.parameters_spam.keys():
                p_spam_given_mess *= self.parameters_spam[word]
            if word in self.parameters_ham.keys():
                p_ham_given_mess *= self.parameters_ham[word]
        return p_spam_given_mess, p_ham_given_mess


class Bayes:
    def __init__(self):
        self.spam_words_count = {}
        self.ham_words_count = {}
        self.spam_emails_count = 0
        self.ham_emails_count = 0
        self.spam = "SPAM"
        self.ham = "OK"

    # call this when training on new mail
    def add_spam_ham_count(self, email_label):
        if email_label == self.spam:
            self.spam_emails_count += 1
        else:
            self.ham_emails_count += 1

    # call this on every word from mail
    def add_word(self, word, email_label):
        if email_label == self.spam:
            self.add_to_dict(self.spam_words_count, word)
        else:
            self.add_to_dict(self.ham_words_count, word)

    # ads count of given word, if word is not in dictionary it adds it there
    def add_to_dict(self, dict, key):
        try:
            dict[key] += 1
        except KeyError:
            dict[key] = 1

    # removes unimportant parts of ham and spam dictionaries
    def clean_dictionaries(self):
        print("ham words:", len(self.ham_words_count.keys()), "spam words:", len(self.spam_words_count.keys()))
        # remove any words with less than min_num occurences
        min_num = 3
        spam_keys = list(self.spam_words_count.keys())
        for i in spam_keys:
            if self.spam_words_count[i] < min_num:
                self.spam_words_count.pop(i)
        ham_keys = list(self.ham_words_count.keys())
        for i in ham_keys:
            if self.ham_words_count[i] < min_num:
                self.ham_words_count.pop(i)
        print("by count", "ham words:", len(self.ham_words_count.keys()), "spam words:", len(self.spam_words_count.keys()))

        # remove words that appear in both spam and ham_filter
        # min_dif_mult = how many times bigger chance must there be to take as substantial evidence
        min_dif_mult = 3
        spam_keys = list(self.spam_words_count.keys())
        for spam_word in spam_keys:
            if spam_word in self.ham_words_count.keys():
                word_spam_perc = self.spam_words_count[spam_word]/self.spam_emails_count
                word_ham_perc = self.ham_words_count[spam_word]/self.ham_emails_count
                if max(word_spam_perc, word_ham_perc) / min(word_spam_perc, word_ham_perc) < min_dif_mult:
                    self.ham_words_count.pop(spam_word)
                    self.spam_words_count.pop(spam_word)
                elif word_spam_perc < word_ham_perc:
                    self.spam_words_count.pop(spam_word)
                else:
                    self.ham_words_count.pop(spam_word)
        print("same in both", "ham words:", len(self.ham_words_count.keys()), "spam words:", len(self.spam_words_count.keys()))


    # txt by mel byt list slov z mailu na ktery se ptame
    def calculate_ham_chance(self, email_text):
        all_emails_count = self.ham_emails_count + self.spam_emails_count
        ham_perc = self.ham_emails_count / all_emails_count
        spam_perc = self.spam_emails_count / all_emails_count
        spam_probability= self.calc_label_probability(self.spam_words_count, self.spam_emails_count, email_text)
        ham_probability= self.calc_label_probability(self.ham_words_count, self.ham_emails_count, email_text)
        #print(ham_probability, spam_probability)
        is_ham_percentage = ham_probability * ham_perc / (ham_probability * ham_perc + spam_probability * spam_perc)
        return is_ham_percentage

    def calc_label_probability(self, words_label_count, emails_label_count, email_text):
        label_probability = SMOOTH_PAR
        for word in words_label_count.keys():
            if word in email_text:
                word_occurence_percentage = words_label_count[word] / emails_label_count
            else:
                word_occurence_percentage = SMOOTH_PAR - words_label_count[word] / emails_label_count
            label_probability *= word_occurence_percentage
        return label_probability





        


            