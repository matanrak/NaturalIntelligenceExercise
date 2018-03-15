# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

# LOG:
# First thing I am going to do is to work on the text & sentence splitting.

import re


def split_text_to_sentences(text):
    return re.split(' *[\.\?!][\'"\)\]]* *', text)


# base regex structure was made by jbernau (github username),
def split_sentences_to_words(sentences):
    regex = re.compile('(?u)' + '|'.join([r'\b' + word + r'(?![\w-])' for word in get_stop_words()]), re.IGNORECASE)
    return [regex.split(sentence) for sentence in sentences]


def get_stop_words():
    try:
        with open('Fox_1989_StopList.txt', 'r') as stop_word_file:
            return [line.strip() for line in stop_word_file.readlines()]
    except IOError:
        return []


# This is the text from Figure 1.1
test_text = "Compatibility of systems of linear constraints over the set of natural numbers . Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types of systems and systems of mixed types."

print(split_sentences_to_words(split_text_to_sentences(test_text)))