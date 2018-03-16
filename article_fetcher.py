from bs4 import BeautifulSoup
import urllib2, os

# The feed fetcher will differentiate articles using this string
split_by = '<item>'


# While technically it is xml,
# feed burner's xml is formatted like html and such it will be more convinient to parse it as HTML
def fetch_feed():

    response = urllib2.urlopen('http://feeds.feedburner.com/TechCrunch').read()
    response_articles = response.split(split_by)
    articles = {}

    for article in [a for a in response_articles if response_articles.index(a) > 0]:

        soup = BeautifulSoup(article.strip(), 'html.parser')
        text_soup = BeautifulSoup(soup.getText(), 'html.parser')

        title = ''.join([tag.string.strip() for tag in soup.findAll("title")])
        text = os.linesep.join([tag.string for tag in text_soup.findAll("p") if tag.string is not None]).replace("-", " ")

        articles.update({title: text})

    return articles
