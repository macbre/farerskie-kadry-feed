import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import TextIO, Optional, Iterable
from os import getenv

from graph_api import iterate_api_responses, make_request, created_time_field_to_datetime
from dotenv import load_dotenv


@dataclass
class InstagramMedia:
    message: str
    permalink_url: str
    full_picture: str
    created_time: datetime
    like_count: Optional[int]

    @staticmethod
    def from_api_entry(post: dict):
        """
        Creates a dataclass instance out of Instagram API response

        https://developers.facebook.com/docs/instagram-api/reference/ig-media#fields
        """
        return InstagramMedia(
            message=post.get('caption', ''),  # there can be only an image shared (i.e. with no message at all)
            permalink_url=post.get('permalink'),
            full_picture=post.get('media_url'),
            created_time=created_time_field_to_datetime(post.get('timestamp')),
            like_count=post.get('like_count')
        )

    def __repr__(self) -> str:
        return f'{self.message[0:96]}... ({self.created_time.isoformat()}) <{self.permalink_url}>'

    def dict(self) -> dict:
        return {
            k: str(v) if v is not None else None
            for k, v in asdict(self).items()
        }


# # https://developers.facebook.com/docs/instagram-api/getting-started#before-you-start
def ig_account_id_for_fb_page(fb_page: str, access_token: str) -> Optional[str]:
    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/
    resp = make_request(f'/v17.0/{fb_page}', req_params={
        'fields': ','.join(
            ['connected_instagram_account{id,name,biography}', 'instagram_accounts{username,id,followed_by_count,media_count,profile_pic}', 'name', 'about']
        ),
        'access_token': access_token,
    })
    logging.info(f'Found IG account for {fb_page}: {repr(resp.get("instagram_accounts"))}, connected one: {repr(resp.get("connected_instagram_account"))}')

    return resp.get('connected_instagram_account', {}).get('id')


def get_instagram_feed(ig_feed_name: str, access_token: str) -> Iterable[InstagramMedia]:
    logger = logging.getLogger('get_instagram_feed')
    logger.info(f'Getting the "{ig_feed_name}" Instagram feed ...')

    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/media#reading
    feed = iterate_api_responses(endpoint=f'/v17.0/{ig_feed_name}/media', req_params={
        'fields': ','.join(
            ['caption', 'media_url', 'timestamp', 'thumbnail_url', 'shortcode', 'permalink', 'like_count']),
        'access_token': access_token,
    })

    for entry in feed:
        yield InstagramMedia.from_api_entry(entry)


def save_feed_to_ndjson(ig_account: str, access_token: str, output: TextIO):
    feed = get_instagram_feed(ig_account, access_token)

    for media in feed:
        logging.info(f'{repr(media)}')

        json.dump(media.dict(), sort_keys=True, fp=output)
        output.write("\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()  # take environment variables from .env.

    # https://developers.facebook.com/docs/instagram-api/getting-started
    token = getenv('FB_TOKEN', default='')
    logging.info(f'Using Facebook token: {token[0:3]}***{token[:3]}')

    instagram_account_id = ig_account_id_for_fb_page(fb_page='FarerskieKadry', access_token=token)  # 17841407952879412

    with open('farerskie_kadry_ig.ndjson', 'wt') as fp:
        save_feed_to_ndjson(ig_account=instagram_account_id, access_token=token, output=fp)
