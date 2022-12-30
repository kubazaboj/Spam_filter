def read_classification_from_file(filename):
    classify_dict = {}
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            classify_dict[line.split()[0]] = line.split()[1]
    return classify_dict


# removes unnecesary characters from text
def skin_text(text):
    text = remove_brackets(text, "<", ">")
    text = remove_brackets(text, "(", ")")
    text = remove_brackets(text, "[", "]")
    text = remove_brackets(text, "{", "}")
    text = remove_special_chars(text)
    return text

# removes brackets or bracketlike parts of text
def remove_brackets(text, start_brack, end_brack):
    text_parts = text.split(start_brack)
    correct = []
    for text_part in text_parts:
        text_split = text_part.split(end_brack)
        if len(text_split) == 1:
            correct.append(text_split[0])
        else:
            correct = correct + text_split[1:]
    return "".join(i for i in correct)


def remove_duplicates(text_list):
    return list(set(text_list))

def remove_long(text_list, max_len):
    return [i for i in text_list if len(i) < max_len]

def remove_special_chars(text):
    to_remove = "_,.;:*-/0123456789"
    for char in to_remove:
        text = text.replace(char, "")
    return text


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
            d[i][j] = min([d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + sub_cost])
    return d[len(w2)][len(w1)]


if __name__ == "__main__":
    text = ""
    with open("train_dir/text1.txt", encoding='utf-8') as f:
        text = skin_text(f.read())
    with open("train_dir/out.txt", mode='w', encoding='utf-8') as f:
        f.write(text)