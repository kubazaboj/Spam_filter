def read_classification_from_file(filename):
    classify_dict = {}
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            classify_dict[line.split()[0]] = line.split()[1]
    return classify_dict
