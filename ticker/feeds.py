import feedparser
import sys

#https://www.nba.com/knicks/rss.xml

def getMetsNews():
    return getFeed('http://mlb.mlb.com/partnerxml/gen/news/rss/nym.xml')

def getNews():
    return getFeed('http://feeds.reuters.com/Reuters/domesticNews')

def getFeed(url):
    msgs = []
    d = feedparser.parse(url)
    i = 0
    for e in d.entries:
        title = e.title
        #rint title
        msgs.append(title)
        i = i + 1
        if (i >= 10):
            break
    return msgs
