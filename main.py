import logging, os, json
import corenlp, article_fetcher, rake

nlp = None


def main():
    try:

        main.nlp = corenlp.StanfordCoreNLP('stanford-corenlp', logging_level=logging.ERROR)

        articles = article_fetcher.fetch_feed()

        i = 0
        for article in articles:
            # For debug purposes I only check one article each time.
            if i is 0:
                print article, os.linesep, os.linesep, articles[article], os.linesep, os.linesep

                text = articles[article]

                rk = rake.Rake(text, main.nlp)
                key_words = rk.get_key_words()

                print key_words

            i += 1


    finally:
        print "Shutting down"
        main.nlp.close()


if __name__ == '__main__':
    main()

