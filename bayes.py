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
    
    """Look how this can be implemented to filter, please"""
    
    def calc_vocab_len(self, vocab_ham, vocab_spam):
        vocab = {**vocab_ham, **vocab_spam}  # Merging ham and spam words dictionary together to have all words in one dictionary
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

    def calc_param_sum_for_email(self, parameters_spam_words, parameters_ham_words, email_words):
        spam_prob = 0
        ham_prob = 0
        for word in email_words:
            spam_prob += parameters_spam_words[word]
            ham_prob += parameters_ham_words[word]
        return spam_prob, ham_prob
    
    def label_message(self, spam_prob, ham_prob):
        if(spam_prob > ham_prob):
            return "SPAM"
        elif(spam_prob < ham_prob):
            return "HAM"
        else:
            return "Same probabilities"

"""The actual Bayes we are using rn"""
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

    # txt by mel byt list slov z mailu na ktery se ptame
    def calculate_ham_chance(self, email_text):
        all_emails_count = self.ham_emails_count + self.spam_emails_count
        ham_perc = self.ham_emails_count / all_emails_count
        spam_perc = self.spam_emails_count / all_emails_count
        spam_probability = self.calc_label_probability(self.spam_words_count, self.spam_emails_count, email_text)
        ham_probability = self.calc_label_probability(self.ham_words_count, self.ham_emails_count, email_text)
        is_ham_percentage = (ham_probability * ham_perc) / (ham_probability * ham_perc + spam_probability * spam_perc)
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
        


            