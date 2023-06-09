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
    text_list = [i.lower() for i in text_list]
    return list(set(text_list))


def remove_long(text_list, max_len):
    return [i for i in text_list if len(i) < max_len]


def remove_special_chars(text):
    to_remove = "\'\"=_,.;:*-0123456789/"
    for char in to_remove:
        text = text.replace(char, "")
    to_isolate = "+&#$?!@"
    for char in to_isolate:
        text = text.replace(char, " " + char + " ")
    return text


if __name__ == "__main__":
    text = ""
    with open("train_dir/text1.txt", encoding='utf-8') as f:
        text = skin_text(f.read())
    text = skin_text(text)
    text = text.split()
    text = remove_duplicates(text)
    remove_long(text, 20)
    with open("train_dir/out.txt", mode='w', encoding='utf-8') as f:
        for i in text:
            f.write(i + " ")