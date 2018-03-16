import logging
import corenlp, article_fetcher, rake

nlp = None


def main():

    articles = article_fetcher.fetch_feed()

    for article in articles:
        print article


if __name__ == "__main__":
    nlp = corenlp.StanfordCoreNLP('stanford-corenlp', logging_level=logging.ERROR)
    main()

