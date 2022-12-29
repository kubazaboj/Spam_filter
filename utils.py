def read_classification_from_file(filename):
    classify_dict = {}
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            classify_dict[line.split()[0]] = line.split()[1]
    return classify_dict


def get_email_derivatives(email):
    email = email.lower()
    # split mail by @
    derivatives = email.split("@")
    # add to derivates without numbers
    derivatives.append(''.join(i for i in derivatives[0] if not i.isdigit()))
    derivatives.append(''.join(i for i in derivatives[1] if not i.isdigit()))
    # add to derivates with nums but no spetial chars
    derivatives.append(''.join(i for i in derivatives[0] if i.isalpha() or i.isdigit()))
    derivatives.append(''.join(i for i in derivatives[1] if i.isalpha() or i.isdigit()))
    # add to derivates without nums and specital characters
    derivatives.append(''.join(i for i in derivatives[0] if i.isalpha()))
    derivatives.append(''.join(i for i in derivatives[1] if i.isalpha()))
    return derivatives


def levenshtein_dist(w1, w2):
    d = [[0 for i in range(len(w1) + 1)] for j in range(len(w2) + 1)]
    for i in range(1, len(w2) + 1):
        d[i][0] = i
    for i in range(1, len(w1) + 1):
        d[0][i] = i
    for i in range(1, len(w2) + 1):
        for j in range(1, len(w1) + 1):
            if w1[j - 1] == w2[i - 1]:
                sub_cost = 0
            else:
                sub_cost = 1
            d[i][j] = min([d[i - 1][j] + 1, d[i][j - 1] + 1, d[i-1][j-1] + sub_cost])
    return d[len(w2)][len(w1)]

if __name__ == "__main__":
    print(get_email_derivatives("spilar.vojta123/!@gmail.com"))
    print(levenshtein_dist("saturday", "sunday"))