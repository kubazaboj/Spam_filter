class Pattern_counter:
    def __init__(self):
        self.importance = {}
        self.char_counts = {}
        self.percentages = {}
        self.caps_count = 0
        self.word_count = 0
        self.letter_count = 0

    # add word to pattern counter and check for all possible patterns
    def add_word(self, word):
        chars_to_check = ["!", "?", "$", "@"]
        self.word_count += 1
        for char in chars_to_check:
            self.check_char(word, char)
        self.check_caps_lock(word)

    # checks if word has capslock if yes adds to caps_count
    def check_caps_lock(self, word):
        for letter in word:
            self.letter_count += 1
            if not letter.islower() and letter.isalpha():
                self.caps_count += 1
                self.add_to_dict(self.importance, "Caps", value=0)

    # check word for charackters, adds to char_counts dictionary
    def check_char(self, word, char):
        for letter in word:
            if letter == char:
                self.add_to_dict(self.char_counts, char)
                self.add_to_dict(self.importance, char, value=0)

    def add_to_dict(self, dict, key, value=1, defaul_value=1):
        try:
            dict[key] += value
        except KeyError:
            dict[key] = defaul_value

    def calculate_percentages(self):
        for key in self.char_counts.keys():
            self.percentages[key] = self.char_counts[key] / self.word_count
        self.percentages["Caps"] = self.caps_count / self.letter_count
        return self.percentages
