# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

from multiprocessing import Pool
import re, os


def unwrapped_candidates_from_sentence(arg, **kwarg):
    return Rake.get_candidates_from_sentence(*arg, **kwarg)


class Rake:

    def __init__(self, text, nlp):

        self.nlp = nlp

        # Removes all non-unicode characters and quotation marks from the text for cleaner sentence splitting
        self.text = text.replace('"', '')
        self.text = re.sub(r'[^\x00-\x7F]+', '', self.text)

        # Although corenlp has sublime sentence splitting, In order to save time I decided to pre split the sentences
        self.sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', self.text)

    def get_key_words(self):

        pool = Pool(processes=8)
        results = pool.map_async(unwrapped_candidates_from_sentence, zip([self]*len(self.sentences), self.sentences))

        pool.close()
        pool.join()

        results = results.get()

        candidates = [candidate for sub_array in results for candidate in sub_array]

        return self.calculate_candidate_scores(candidates)

    def get_candidates_from_sentence(self, sentence_string):

        candidates = []

        try:
            sentence = self.nlp.parse(annotators='depparse pos', data=sentence_string)['sentences'][0]

            for index in xrange(0, len(sentence['tokens'])):

                # Verifying that a word is a noun
                if not sentence['tokens'][index]['pos'].startswith('N'):
                    continue

                phrase = {sentence['tokens'][index]['word']: index}

                phrase.update(
                    {entity['dependentGloss']: entity['dependent'] - 1
                     for entity in sentence['basicDependencies']
                     if entity['governor'] - 1 is index
                     and entity["dep"] in ['compound', 'amod']
                     or sentence['tokens'][entity['dependent'] - 1]['pos'] is 'POS'
                     })

                phrase = sorted(phrase.items(), key=lambda (key, value): value)
                phrase = ' '.join([part[0] for part in phrase]).strip()

                candidates.append(phrase)

        except (IndexError, UnicodeError) as exception:
            print 'Failed to parse: ', sentence, os.linesep, exception

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
