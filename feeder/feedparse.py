import pickle
import feedparser
import time
from os import path

here = path.dirname(__file__) + path.sep


def myparser(ChannelID):
    with open(here + 'channels.pickle', 'rb') as f:
        channels = pickle.load(f)
    try:
        d = feedparser.parse(channels[ChannelID][1])
        if not d.feed:
            raise Exception('Cann\'t link to Internet')
        channel = {}
        channel['title'] = d.feed.get('title', 'No title')
        channel['link'] = d.feed.get('link', 'No link')
        channel['description'] = d.feed.get('description', 'No description')
        channel['items'] = []

        for ditem in d.entries:
            item = {}
            item['title'] = ditem.get('title', 'No title')
            item['link'] = ditem.get('link', 'No link')
            item['description'] = ditem.get('description', 'No description')
            item['pubDate'] = ditem.get('published_parsed', None)
            channel['items'].append(item)
        channel['items'].sort(key=lambda item: item['pubDate'], reverse=True)

        with open(here + 'pickles/' + channels[ChannelID][0] + '.pickle', 'wb') as f:
            pickle.dump(channel, f)
    except Exception as e:
        print(e)
        return (channels[ChannelID][0], -1)
    else:
        return (channels[ChannelID][0], 1)


def myrender(item):
    htmlstr = '''<html><head>
                <title>''' + item['title'] + '''</title>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <link rel="stylesheet" type="text/css" href=''' + '"' + __file__ + '''/../css/GitHub2.css"/>
                </head>
                <body><center>
                <h1>''' + item['title'] + '</h1>' + time.strftime('%Y-%m-%d %H:%M:%S', item['pubDate']) + '''
                </center><hr/>''' + item['description'] + '''
                <div><a href=''' + item['link'] + '''>查看原文</a></div>
                </body>
                </html>'''
    return htmlstr

if __name__ == '__main__':
    myparser(0)
