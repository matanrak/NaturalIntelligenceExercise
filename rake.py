# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

# LOG:
# First thing I am going to do is to work on the text & sentence splitting.
# Fixed split_sentences_to_words, now it returns a flat array and not an array inside another
# Added calculate_candidate_scores

import re


def get_stop_words():
    try:
        with open('Fox_1989_StopList.txt', 'r') as stop_word_file:
            return [line.strip() for line in stop_word_file.readlines()]
    except IOError:
        return []


# base regex structure was made by jbernau (github username)
def get_candidates_from_text(text):

    sentences = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s').split(text)
    regex = re.compile('|'.join([r'\b' + word + r'(?![\w-])' for word in get_stop_words()]), re.IGNORECASE)

    return [word.strip() for sen in sentences for word in regex.split(sen) if word != '' and len(word) > 1]


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


# This is the text from Figure 1.1
test_text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."
