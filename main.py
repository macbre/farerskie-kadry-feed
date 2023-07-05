import logging
import json
from os import getenv
from typing import TextIO

from feed import get_facebook_feed


# http://ndjson.org/
def save_feed_to_ndjson(feed_name: str, token: str, output: TextIO):
    posts = get_facebook_feed(feed_name, token)

    for post in posts:
        logging.info(f'{repr(post)}')

        json.dump(post.dict(), sort_keys=True, fp=output)
        output.write("\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    token = getenv('FB_TOKEN', default='')
    logging.info(f'Using Facebook token: {token[0:3]}***{token[:3]}')

    with open('farerskie_kadry.ndjson', 'wt') as fp:
        save_feed_to_ndjson(feed_name='FarerskieKadry', token=token, output=fp)
