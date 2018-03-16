# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

import re


# base regex structure was made by jbernau (github username)
def get_candidates_from_text(text):

    sentences = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s').split(text)

    # TODO (Soon) use corenlp to find candidates instead of the archaic stop word file method

    return []


# Calculates the score of each candidate phrase as the sum of each of it's word's scores
def calculate_candidate_scores(candidates):

    all_words = [word for candidate in candidates for word in re.split('\s+', candidate)]
    frequency_dict = {word: 0 for word in all_words}
    degree_dict = frequency_dict.copy()

    for can in candidates:
        words = re.split('\s+', can)
        degree = len(words) - 1
        for word in words:
            frequency_dict[word] += 1
            degree_dict[word] += degree

    word_scores = {word: (frequency_dict[word] + degree_dict[word]) / (frequency_dict[word]) for word in all_words}
    candidate_scores = {candidate: sum([word_scores[word] for word in re.split('\s+', candidate)]) for candidate in candidates}

    return sorted(candidate_scores.items(), key=lambda (key, value): value, reverse=True)


def get_key_words(text):
    try:
        candidates = get_candidates_from_text(text)
        print "can: ", candidates
        return calculate_candidate_scores(candidates)
    except UnicodeError:
        return []
