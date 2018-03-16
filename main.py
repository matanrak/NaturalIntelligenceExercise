import logging, os
import corenlp, article_fetcher, rake

nlp = None


def main():

    articles = article_fetcher.fetch_feed()

    i = 0
    for article in articles:
        if i is 0:
            print article, os.linesep, os.linesep, articles[article], os.linesep, os.linesep
            parsed = nlp.parse(articles[article])
            print parsed
        i += 1


if __name__ == "__main__":
    nlp = corenlp.StanfordCoreNLP('stanford-corenlp', logging_level=logging.ERROR)
    main()

