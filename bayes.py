SMOOTH_PAR = 1 #Smoothing parametr for calcuclating the probability of ham/spam
if __name__ == "__main__":
    train_emails = {} #The dictionary of training emails and their labels
    labels_filename = "" #Filename of the txt with the filenames and labels
    #Opening the prediction to get the dictionary of emails and their label
    with open(labels_filename, 'r', encoding='utf-8') as labels_file:
        for line in labels_file:
            train_emails[line[0]]= line[1]
    spam_messages = [spam for spam in train_emails.keys() if train_emails[spam] == "SPAM"]
    ham_messages = [ham for ham in train_emails.keys() if train_emails[ham] == "HAM"]
    no_of_emails= len(train_emails) #Total number of all emails
    pct_spam = len(spam_messages) / no_of_emails #The percantage of spam emails in the training set
    pct_ham = len(ham_messages) / no_of_emails #The percantage of ham emails in the training set
    vocab_spam = {}
    vocab_ham = {}
    no_words_spam = 0 #Total number of words in all spam messages
    no_words_ham = 0 #Total number of words in all ham messages
    for email_file in train_emails.keys():
        with open(email_file, 'r', encoding='utf-8') as email:
            #Clean the email from html tags and have only body...
            #Then create a vocabulary dictionary
            for line in email:
                for word in line:
                    if train_emails[email_file] == "SPAM":
                        no_words_spam +=1
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
                            
    vocab = {**vocab_ham, **vocab_spam}#Merging ham and spam words dictionary together to have all words in one dictionary   
    vocab_len =  len(vocab)#Total number of words in both, ham and spam words dictionaries
    parameters_spam_words = {} #The dictionary of parameters for all words in spam messages 
    parameters_ham_words = {} #The dictionary of parameters for all words in ham messages 
    
    for word in vocab_ham:
        par_ham_word_given = (vocab_ham[word] + SMOOTH_PAR) / (no_words_spam + SMOOTH_PAR * vocab_len)
        #Counting the parametr value for specified ham word in the dictionary
        parameters_ham_words[word] = par_ham_word_given
        #Adding the parameter to the dictionary of all ham words parameters in the dictionary
    for word in vocab_spam:
        par_spam_word_given = (vocab_ham[word] + SMOOTH_PAR) / (no_words_spam + SMOOTH_PAR * vocab_len)
        #Counting the parametr value for specified spam word in the dictionary
        parameters_spam_words[word] = par_spam_word_given
        #Adding the parameter to the dictionary of all spam words parameters in the dictionary
        

"""The searching in the dictionary"""
#To be done, I honestly tried, but no clue how to exactly calculate it
        
    
            
            
    
    
    
            