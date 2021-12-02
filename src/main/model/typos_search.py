from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance


def find_typos(text, words=None):
    text = text.lower()
    rate = 1.0
    final_word = text
    for word in words:
        new_rate = normalized_damerau_levenshtein_distance(text, word)
        if new_rate < rate:
            final_word = word
            rate = new_rate
    if rate > 0.40:
        return False
    if rate == 0.0:
        return True
    return True