SMOOTH_PAR = 1  # Smoothing parametr for calcuclating the probability of ham/spam


class Bayes:
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


"""The searching in the dictionary"""
# To be done, I honestly tried, but no clue how to exactly calculate it


''' navrh na zmenu '''


class Bayes2:
    def __init__(self):
        self.word_spam_count = {}
        self.word_ham_count = {}
        self.spam_count = 0
        self.ham_count = 0
        self.spam = "SPAM"
        self.ham = "OK"

    # call this when training on new mail
    def add_spam_ham_count(self, spam_ham):
        if spam_ham == self.spam:
            self.spam_count += 1
        else:
            self.ham_count += 1

    # call this on every word from mail
    def add_word(self, word, spam_ham):
        if spam_ham == self.spam:
            self.add_to_dict(self.word_spam_count, word)
        else:
            self.add_to_dict(self.word_ham_count, word)

    # ads count of given word, if word is not in dictionary it adds it there
    def add_to_dict(self, dict, key):
        try:
            dict[key] += 1
        except KeyError:
            dict[key] = 1

    # txt by mel byt list slov z mailu na ktery se ptame
    def calculate_ham_chance(self, text):
        spam_result = 1
        ham_result = 1
        ham_perc = self.ham_count / (self.ham_count + self.spam_count)
        spam_perc = self.spam_count / (self.ham_count + self.spam_count)
        for word in self.word_spam_count.keys():
            if word in text:
                to_mult = self.word_spam_count[word] / self.spam_count
            else:
                to_mult = 1 - self.word_spam_count[word] / self.spam_count
            if to_mult < 1/self.spam_count:
                to_mult = 1
            spam_result *= to_mult
        for word in self.word_ham_count.keys():
            if word in text:
                to_mult = self.word_ham_count[word] / self.ham_count
            else:
                to_mult = 1 - self.word_ham_count[word] / self.ham_count
            if to_mult < 1/self.ham_count:
                to_mult = 1
            ham_result *= to_mult
        if ham_result > spam_result:
            return 1
        else:
            return 0
        is_ham_percentage = ham_result * ham_perc / (ham_result * ham_perc + spam_result * spam_perc)
        return is_ham_percentage


            