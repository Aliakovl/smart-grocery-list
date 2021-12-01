from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance


def find_typos(text, words=None):
    text = text.lower()
    if words is None:
        words = ['привет', 'яблоко', 'сметана']
    rate = 1.0
    final_word = text
    for word in words:
        new_rate = normalized_damerau_levenshtein_distance(text, word)
        if new_rate < rate:
            final_word = word
            rate = new_rate
    if rate > 0.40:
        return text
    if rate == 0.0:
        return text
    return final_word


print(find_typos('Привет'))
print(find_typos('Првет'))
print(find_typos('Прывет'))
print(find_typos('Яблко'))
print(find_typos('Првд'))
