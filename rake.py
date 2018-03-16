# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

import re


class Rake:

    def __init__(self, text, nlp):
        self.text = text
        self.nlp = nlp
        self.parsed = nlp.parse(text)
        self.sentences = self.parsed['sentences']

    def get_key_words(self):
        try:
            candidates = self.get_candidates_from_text()
            return self.calculate_candidate_scores(candidates)
        except UnicodeError:
            return []

    def get_candidates_from_text(self):

        candidates = []

        for sentence in self.sentences:
            for index in xrange(0, len(sentence['tokens'])):

                # Verifying that a word is a noun
                if not sentence['tokens'][index]['pos'].startswith('N'):
                    continue

                phrase = {sentence['tokens'][index]['word']: index}
                phrase.update(
                    {entity['dependentGloss']: entity['dependent']
                     for entity in sentence['basicDependencies']
                     if entity['governor'] - 1 is index
                     and entity["dep"] in ['compound', 'amod']
                     or sentence['tokens'][entity['dependent'] - 1]['pos'] is 'POS'
                     })

                phrase = sorted(phrase.items(), key=lambda (key, value): value)
                phrase = ' '.join([part[0] for part in phrase]).strip()

                candidates.append(phrase)

        return candidates

    # Calculates the score of each candidate phrase as the sum of each of it's word's scores
    @staticmethod
    def calculate_candidate_scores(candidates):

        all_words = [word for candidate in candidates for word in candidate.split()]
        frequency_dict = {word: 0 for word in all_words}
        degree_dict = frequency_dict.copy()

        for can in candidates:
            words = can.split()
            degree = len(words) - 1
            for word in words:
                frequency_dict[word] += 1
                degree_dict[word] += degree

        scores = {word: (frequency_dict[word] + degree_dict[word]) / (frequency_dict[word]) for word in all_words}
        candidate_scores = {candidate: sum([scores[word] for word in candidate.split()]) for candidate in candidates}

        return sorted(candidate_scores.items(), key=lambda (key, value): value, reverse=True)
