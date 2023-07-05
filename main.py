import logging
from os import getenv
from feed import get_facebook_feed

def get_feed(feed_name: str, token: str):
    posts = get_facebook_feed(feed_name, token)

    for post in posts:
        logging.info(f'{repr(post)}')



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    token = getenv('FB_TOKEN', default='')
    logging.info(f'Using Facebook token: {token[0:3]}***{token[:3]}')

    get_feed(feed_name='FarerskieKadry', token=token)
