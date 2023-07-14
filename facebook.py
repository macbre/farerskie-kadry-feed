# Provides Facebook Feed API features
#
# https://developers.facebook.com/docs/graph-api/reference/v2.0/post
import logging
import re
from dataclasses import dataclass
from typing import Optional, Iterable
from urllib.parse import urlparse, parse_qs

from graph_api import iterate_api_responses, created_time_field_to_datetime, ResponseEntity


@dataclass
class FacebookPost(ResponseEntity):
    link: Optional[str]

    @staticmethod
    def from_api_entry(post: dict):
        """
        Creates a dataclass instance out of Facebook API response

        https://developers.facebook.com/docs/graph-api/reference/v2.0/post#fields
        """
        return FacebookPost(
            message=post.get('message', ''),  # can be empty if just re-sharing a post
            permalink_url=post.get('permalink_url'),
            full_picture=post.get('full_picture'),
            created_time=created_time_field_to_datetime(post.get('created_time')),
            link=None
        )


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

    for entry in feed:
        logger.debug(f'Post: {entry}')

        try:
            # 'attachments': {'data': [{'url': 'https://l.facebook.com/l.php?u=https%3A%2F%2Ffare ...
            link = entry.get('attachments').get('data')[0].get('url')

            if '//l.facebook.com' not in link:
                raise KeyError

            # parse the outgoing link
            parsed = urlparse(link)
            link = parse_qs(parsed.query)['u'][0]

        except (KeyError, AttributeError):
            link = None

        post = FacebookPost.from_api_entry(entry)
        post.link = link

        yield post


def get_first_hashtag(text: str) -> Optional[str]:
    """
    'So, #Víkarbyrgi and #Hamrabyrgi' -> Víkarbyrgi
    """
    matches = re.search(r'#([^\s]+)', text)
    return matches.group(1).rstrip(',.') if matches else None


def paragraphize(text: str) -> str:
    """
    Turns:

    foo

    bar

    into:
    <p>foo</p><p>bar</p>
    """
    return '<p>' + re.sub(r'\n\n', '</p>\n<p>', text) + '</p>' if text else ''
