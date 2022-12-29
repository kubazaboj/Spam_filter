class BinaryConfusionMatrix:
    def __init__(self, pos_tag, neg_tag):
        self.TP = 0
        self.TN = 0
        self.FP = 0
        self.FN = 0
        self.pos_tag = pos_tag
        self.neg_tag = neg_tag

    def as_dict(self):
        return {"tp": self.TP, "tn": self.TN, "fp": self.FP, "fn": self.FN}

    def update(self, truth, prediction):
        if not (truth == self.pos_tag or truth == self.neg_tag) or not (
                prediction == self.pos_tag or prediction == self.neg_tag):
            raise ValueError
        else:
            # pos
            if truth == self.pos_tag:
                # pos pos
                if prediction == self.pos_tag:
                    self.TP += 1
                # pos neg
                else:
                    self.FN += 1
            # neg
            else:
                # neg pod
                if prediction == self.pos_tag:
                    self.FP += 1
                # neg neg
                else:
                    self.TN += 1

    def compute_from_dicts(self, truth_dict, pred_dict):
        for key in truth_dict.keys():
            self.update(truth_dict[key], pred_dict[key])


if __name__ == "__main__":
    truth_dict = {'em1': 'SPAM', 'em2': 'SPAM', 'em3': 'OK', 'em4': 'OK'}
    pred_dict = {'em1': 'SPAM', 'em2': 'OK', 'em3': 'OK', 'em4': 'SPAM'}
    cm2 = BinaryConfusionMatrix(pos_tag='SPAM', neg_tag='OK')
    cm2.compute_from_dicts(truth_dict, pred_dict)
    print(cm2.as_dict())
