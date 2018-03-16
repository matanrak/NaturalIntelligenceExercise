from bs4 import BeautifulSoup
import urllib2, os
import rake, nlp


# The feed fetcher will differentiate articles using this string
split_by = '<item>'


# While technically it is xml,
# feed burner's xml is formatted like html and such it will be more convinient to parse it as HTML
def fetch_feed():

    response = urllib2.urlopen('http://feeds.feedburner.com/TechCrunch').read()
    articles = response.split(split_by)

    for article in [a for a in articles if articles.index(a) == 1]:

        soup = BeautifulSoup(article.strip(), 'html.parser')
        text_soup = BeautifulSoup(soup.getText(), 'html.parser')

        title = ''.join([tag.string.strip() for tag in soup.findAll("title")])
        text = os.linesep.join([tag.string for tag in text_soup.findAll("p") if tag.string is not None]).replace("-", " ")

        key_words = rake.get_key_words(text)

        print title, os.linesep, text, os.linesep, os.linesep, "Key words: " + os.linesep

        for key_word in [kw for kw in key_words if key_words.index(kw) < 5]:
            print key_word[0], ": ", key_word[1]

        print os.linesep + os.linesep + os.linesep


fetch_feed()
