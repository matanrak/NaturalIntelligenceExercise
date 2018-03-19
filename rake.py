# Based on the RAKE algorithm
# Created in 2010 by S. Rose, D. Engel, N. Cramer and W. Cowley
# https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf

from multiprocessing import Pool
import re
import os
import json


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

        parsed = self.nlp.parse(annotators='depparse, pos, ner', data=text)['sentences'][0]
        print text
        print json.dumps(parsed)

    def get_key_words(self):

        pool = Pool(processes=4)

        results = pool.map_async(unwrapped_candidates_from_sentence, zip([self]*len(self.sentences), self.sentences))

        pool.close()
        pool.join()

        candidates = {key: value for result in results.get() for key, value in result.items()}

        return self.calculate_candidate_scores(candidates)

    def get_candidates_from_sentence(self, sentence_string):

        candidates = {}

        try:
            sentence = self.nlp.parse(annotators='depparse, pos, ner', data=sentence_string)['sentences'][0]

            for index in xrange(0, len(sentence['tokens'])):
                try:
                    tokens = sentence['tokens']

                    # Verifying that a word is a noun
                    if not tokens[index]['pos'].startswith('N'):
                        continue

                    phrase = {tokens[index]['word']: index}

                    phrase.update({entity['dependentGloss']: entity['dependent'] - 1
                                   for entity in sentence['basicDependencies']
                                   if entity['governor'] - 1 is index
                                   and entity["dep"] in ['compound', 'amod']
                                   and tokens[entity['dependent'] - 1]['pos'] not in ['VBG', 'VBZ']
                                   or tokens[entity['dependent'] - 1]['pos'] is 'POS'
                                   and entity['governor'] - 1 is index
                                   })

                    phrase = sorted(phrase.items(), key=lambda (k, v): v)
                    phrase = ' '.join([part[0] for part in phrase]).strip()

                    candidates.update({phrase: False})

                except (IndexError, UnicodeError, TypeError) as exception:
                    print 'Failed at (', index, ') ', sentence_string, os.linesep, exception

            # Often; named-entities are a focus of a sentence, so, they should be treated as a standalone phrase
            for entity in [entity for entity in sentence['entitymentions']]:
                if entity['ner'] in ['PERSON', 'ORGANIZATION']:
                    candidates.update({entity['text']: True})
                    print "entity: ",  entity['text']

        except (IndexError, UnicodeError, KeyError) as exception:
            print 'Failed to parse ', sentence_string, os.linesep, exception

        return candidates

    # Calculates the score of each candidate phrase as the sum of each of it's word's scores
    @staticmethod
    def calculate_candidate_scores(candidates_dict):

        all_words = [word.lower() for key, value in candidates_dict.items() for word in key.split()]

        # Initializing all the dictionaries in-order to reduce the need for None handling
        candidate_scores = {key: 0 for key, value in candidates_dict.items()}
        frequency_dict = {word: 0 for word in all_words}
        degree_dict = frequency_dict.copy()
        scores = frequency_dict.copy()

        # I define a possible focus word as a any single Named-Entity
        focus_word_candidates = [key for key, value in candidates_dict.items() if value]

        print "Focus words ", focus_word_candidates

        candidates = [key for key, value in candidates_dict.items() if key not in focus_word_candidates]

        # This is the original RAKE algorithm, it favours long phrases.
        # RAKE uses two main factor to determine a word's score the frequency of the word and it's degree.
        # The frequency of a word or freq(w) is the number occurrences inside candidate phrases.
        # The degree of a word or deg(w) is the sum of the lengths of the candidates the word occurs in.
        for candidate_phrase in candidates:

            candidate_words = candidate_phrase.lower().split()

            for candidate_word in candidate_words:
                frequency_dict[candidate_word] += 1
                degree_dict[candidate_word] += len(candidate_words) - 1

        try:
            # The final score of a word is the ratio of the deg(w) to freq(w)
            scores.update({word: (degree_dict[word] / (frequency_dict[word])) for word in all_words
                           if degree_dict[word] > 0 and frequency_dict[word] > 0})

            # The final score of each candidate is the sum of the score of all it's sons
            candidate_scores.update({cand: sum([scores[word.lower()] for word in cand.split()]) for cand in candidates})

            # This is a modification I made to RAKE that favours short but frequent focus words,
            # Often in news and media; shorter buzzwords are a focus of an article.
            # RAKE was designed to favour longer phrases, although this works great for books and long articles,
            # it does not work well with the short headlines and rss feed articles I set to summarize.
            # In order to improve RAKE's ability to summarize rss feeds I modified it.
            for focus_word in focus_word_candidates:

                containing_candidates = [cand for cand in candidates
                                         if focus_word.lower() in cand.lower()
                                         and candidate_scores[cand]]

                print "i'm here ", focus_word, " : ", len(containing_candidates)\
                    , " before: ", candidate_scores[focus_word]

                for con_cand in containing_candidates:
                        candidate_scores.update({focus_word: candidate_scores[focus_word] + candidate_scores[con_cand]})

                print "after: ", candidate_scores[focus_word]

        except KeyError as exception:
            print 'Failed to set scores', exception

        return sorted(candidate_scores.items(), key=lambda (k, v): v, reverse=True)
