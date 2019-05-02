import feedparser
import sys

#https://www.nba.com/knicks/rss.xml
#https://www.alphavantage.co/ through HA?

def getMetsNews():
    return getFeed('https://www.mlb.com/mets/feeds/news/rss.xml')

def getNews():
    return getFeed('http://feeds.reuters.com/Reuters/domesticNews')


def getScores(l):
    fname = "scores/"+l + ".dat"
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

def getFeed(url):
    msgs = []
    d = feedparser.parse(url)
    i = 0
    for e in d.entries:
        title = e.title
        #rint title
        msgs.append(title)
        i = i + 1
        if (i >= 5):
            break
    return msgs
