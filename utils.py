import re
from typing import Optional

from graph_api import ResponseEntity
from rss import RssFeedItem


def get_first_hashtag(text: str) -> Optional[str]:
    """
    Returns the first hashtag from the text provided (None if none found)

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


def response_entity_to_rss_item(entity: ResponseEntity) -> RssFeedItem:
    """
    Converts and formats the entity from the Facebook feed (FB post / Instagram media)
    to the item for the RSS feed.
    """
    hashtag = get_first_hashtag(entity.message)
    title = ('#' + hashtag) if hashtag else (entity.message[0:32] + '...')

    description = f'<p><img src="{entity.full_picture}" style="max-width: 500px; max-height: 500px" class="fb-feed-image"></p>' if entity.full_picture else ''
    description += f'\n{paragraphize(entity.message)}'

    return RssFeedItem(
        title=title,
        link=entity.permalink_url,
        description=description,
        published=entity.created_time,
    )
