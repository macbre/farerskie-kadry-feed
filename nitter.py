# Uses nitter.net Twitter lightweight UI to fetch all tweets for a given account
# https://nitter.net/ForoysktDaily
import json
import logging
import re
from typing import Iterable
from dataclasses import dataclass

from requests import Session
from rss import RssFeedWriter


def iter_tweets(account: str) -> Iterable:
    http = Session()
    http.headers['user-agent'] = 'py-nitter-feed'

    cursor = ''

    while True:
        url = f'https://nitter.net/{account}?cursor={cursor}'
        resp = http.get(url)

        resp.raise_for_status()

        # <div class="show-more"><a href="?cursor=DAABCgABGEsQd-c__9MKAAIWXMiILRYAAggAAwAAAAIAAA">Load more</a></div>
        cursor = re.search(r'<a href="\?cursor=([^"]+)">Load more</a>', resp.text)
        print(cursor)

        break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # save to the RSS feed
    with open('docs/ForoysktDaily.xml', 'wt') as fp:
        with RssFeedWriter(
                out=fp,
                title='ForoysktDaily on Twitter',
                link='https://nitter.net/ForoysktDaily',
                description='🇫🇴 Faroese Word of the Day'
        ) as feed:
            for tweet in iter_tweets(account='ForoysktDaily'):
                print(tweet)

    logging.info('Done')
