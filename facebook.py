# Provides Facebook Feed API features
#
# https://developers.facebook.com/docs/graph-api/reference/v2.0/post
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from time import strptime
from typing import Optional, Iterable
from urllib.parse import urlparse, parse_qs

from feed import iterate_api_responses

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

    def dict(self) -> dict:
        return {
            k: str(v) if v is not None else None
            for k, v in asdict(self).items()
        }


def get_facebook_feed(feed_name: str, token: str) -> Iterable[FacebookPost]:
    """
    Returns all posts from a given Facebook feed
    """
    logger = logging.getLogger('get_facebook_feed')
    logger.info(f'Getting the "{feed_name}" FB feed ...')

    feed = iterate_api_responses(endpoint=f"/v17.0/{feed_name}/feed", req_params={
        'fields': ','.join(
            ['full_picture', 'message', 'created_time', 'shares', 'permalink_url', 'attachments{url}']
        ),
        'access_token': token,
    })

    for post in feed:
        logger.debug(f'Post: {post}')

        try:
            # 'attachments': {'data': [{'url': 'https://l.facebook.com/l.php?u=https%3A%2F%2Ffare ...
            link = post.get('attachments').get('data')[0].get('url')

            if '//l.facebook.com' not in link:
                raise KeyError

            # parse the outgoing link
            parsed = urlparse(link)
            link = parse_qs(parsed.query)['u'][0]

        except (KeyError, AttributeError):
            link = None

        yield FacebookPost(
            message=post.get('message', ''),  # can be empty if just re-sharing a post
            permalink_url=post.get('permalink_url'),
            full_picture=post.get('full_picture'),
            created_time=datetime(*(strptime(post.get('created_time'), DATE_FORMAT)[0:6])),
            link=link,
        )
