import logging
import json
from itertools import islice
from os import getenv
from typing import TextIO

from dotenv import load_dotenv

from facebook import get_facebook_feed
from rss import RssFeedWriter
from utils import response_entity_to_rss_item


# http://ndjson.org/
def save_feed_to_ndjson(feed_name: str, access_token: str, output: TextIO):
    for entry in get_facebook_feed(feed_name, access_token):
        logging.info(f'{repr(entry)}')

        json.dump(entry.dict(), sort_keys=True, fp=output)
        output.write("\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()  # take environment variables from .env.

    # https://developers.facebook.com/tools/accesstoken/
    # https://developers.facebook.com/tools/debug/accesstoken/
    # https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/#long-lived-page-token
    token = getenv('FB_TOKEN', default='')
    logging.info(f'Using Facebook token: {token[0:3]}***{token[:3]}')

    # with open('farerskie_kadry.ndjson', 'wt') as fp:
    #     save_feed_to_ndjson(feed_name='FarerskieKadry', access_token=token, output=fp)

    # save to the RSS feed
    with open('docs/facebook.xml', 'wt') as fp:
        with RssFeedWriter(
                out=fp,
                title='Farerskie Kadry na Facebooku',
                link='https://www.facebook.com/FarerskieKadry/',
                description='Suma miliona drobnych, banalnych sytuacji, miejsc, '
                            'ludzi uwiecznionych na cyfrowych kadrach i w nostalgicznych zakamarkach pamięci'
        ) as feed:
            ig_feed = islice(get_facebook_feed(feed_name='FarerskieKadry', token=token), 30)

            for post in ig_feed:
                # do not add posts that share links from the blog
                if post.link and 'farerskiekadry.pl' in post.link:
                    continue

                feed.add_item(
                    response_entity_to_rss_item(post)
                )

    logging.info('Done')
