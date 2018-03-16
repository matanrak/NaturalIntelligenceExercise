import logging, os, json
import corenlp, article_fetcher, rake


def main():

    with corenlp.StanfordCoreNLP('stanford-corenlp') as nlp:

        articles = article_fetcher.fetch_feed()

        i = 0
        for article in articles:
            # For debug purposes I only check one article each time.
            if i is 0:
                print article, os.linesep, os.linesep, articles[article], os.linesep, os.linesep

                text = articles[article]

                rk = rake.Rake(text, nlp)
                key_words = rk.get_key_words()

                print key_words

            i += 1


if __name__ == '__main__':
    main()

