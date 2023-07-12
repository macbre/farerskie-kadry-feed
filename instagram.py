import json
import logging
from typing import TextIO, Optional
from os import getenv

from graph_api import iterate_api_responses, make_request
from dotenv import load_dotenv


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


def save_feed_to_ndjson(ig_account: str, access_token: str, output: TextIO):
    logging.info(f'Using IG account: {ig_account}')

    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/media#reading
    feed = iterate_api_responses(endpoint=f'/v17.0/{ig_account}/media', req_params={
        'fields': ','.join(
            ['caption', 'media_url', 'timestamp', 'thumbnail_url', 'shortcode', 'permalink', 'like_count']),
        'access_token': access_token,
    })

    for item in feed:
        logging.info(
            f'{item["timestamp"]} / {item["like_count"]} likes | {item.get("caption", "")} ({item["timestamp"]}) <{item["permalink"]}>',
            item)

        data = {
            'message': item.get("caption", ""),  # there can be only an image shared (i.e. with no message at all)
            'created_time': item["timestamp"],
            'permalink_url': item["permalink"],
            'full_picture': item.get('media_url'),
        }

        json.dump(data, sort_keys=True, fp=output)
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
