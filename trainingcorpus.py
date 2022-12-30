from corpus import Corpus


class TrainingCorpus(Corpus):
    def get_train_emails(self):
        file = "!truth.txt"
        with open(self.dirname + "/" + file, encoding='utf-8') as f:
            yield file, f.read()

    def get_train_file_name(self):
        return self.dirname + "/" + "!truth.txt"