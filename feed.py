# Provides Facebook Feed API features
#
# https://developers.facebook.com/docs/graph-api/reference/v2.0/post
import logging
from dataclasses import dataclass
from datetime import datetime
from time import strptime
from typing import Optional, Iterable
from urllib.parse import urlencode

from requests import Session

# e.g. 2023-02-27T14:31:39+0000
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


@dataclass
class FacebookPost:
    message: str
    permalink_url: str
    full_picture: str
    created_time: datetime
    link: Optional[str]

    def __repr__(self) -> str:
        return f'{self.message[0:96]}... ({self.created_time.isoformat()}) <{self.permalink_url}>'


def _build_api_url(feed_name: str, fields: list[str], token: str) -> str:
    path = f"https://graph.facebook.com/v17.0/{feed_name}/feed"
    query = urlencode(dict(
        pretty=0,
        fields=','.join(fields),
        limit=25,
        access_token=token,
    ))

    return f'{path}?{query}'


def get_facebook_feed(feed_name: str, token: str) -> Iterable[FacebookPost]:
    """
    Returns all posts from a given Facebook feed
    """
    logger = logging.getLogger('get_facebook_feed')

    logger.info(f'Getting the "{feed_name}" FB feed ...')

    http = Session()
    http.headers['user-agent'] = 'py-facebook-feed'

    url = _build_api_url(
        feed_name=feed_name,
        fields=[
            'full_picture',
            'message',
            'created_time',
            'shares',
            'permalink_url',
            'attachments{url}'
        ],
        token=token
    )

    posts_counter = 0

    # iterate through all pages
    while True:
        resp = http.get(url)
        resp.raise_for_status()
        data = resp.json()

        logger.debug(f'Got JSON response: {data}')

        for post in data.get('data', []):
            logger.debug(f'Post: {post}')

            try:
                # 'attachments': {'data': [{'url': 'https://l.facebook.com/l.php?u=https%3A%2F%2Ffare ...
                link = post.get('attachments').get('data')[0].get('url')

            except (KeyError, AttributeError):
                link = None

            yield FacebookPost(
                message=post.get('message', ''),  # can be empty if just re-sharing a post
                permalink_url=post.get('permalink_url'),
                full_picture=post.get('full_picture'),
                created_time=datetime(*(strptime(post.get('created_time'), DATE_FORMAT)[0:6])),
                link=link,
            )

            posts_counter += 1

        # do we have a next page
        next_url = data.get('paging', {}).get('next')

        if next_url is None:
            break

        logger.info('Found next page')
        url = next_url

    logger.info(f'Found {posts_counter} posts')
