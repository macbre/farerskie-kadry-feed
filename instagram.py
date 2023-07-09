import logging
from requests import Session
from os import getenv

from feed import iterate_api_responses

from dotenv import load_dotenv


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()  # take environment variables from .env.

    # https://developers.facebook.com/docs/instagram-api/getting-started
    token = getenv('FB_TOKEN', default='')
    logging.info(f'Using Facebook token: {token[0:3]}***{token[:3]}')

    instagram_user_id = '1918062444917837'
    instagram_account_id = '17841407952879412'
    fb_page = 'farerskie.kadry'

    logging.info(f'Using IG user: {instagram_user_id}')
    logging.info(f'Using IG account: {instagram_account_id}')

    # https://developers.facebook.com/docs/instagram-api/reference/ig-user/media#reading
    feed = iterate_api_responses(endpoint=f'/v17.0/{instagram_account_id}/media', req_params={
        'fields': ','.join(['caption', 'media_url', 'timestamp', 'thumbnail_url', 'shortcode', 'permalink', 'like_count']),
        'access_token': token,
    })

    for item in feed:
        # logging.info(f'Item: %r', item)
        logging.info(f'{item["timestamp"]} / {item["like_count"]} likes | {item.get("caption", "")} ({item["timestamp"]}) <{item["permalink"]}>', item)

    # https://developers.facebook.com/docs/instagram-api/getting-started#before-you-start - you need a pro IG account
    # an your FB access token needs to have the 'instagram_basic' right
    # resp = http.get(f'https://graph.facebook.com/v17.0/{fb_page}', params={
    #     'fields': ','.join(['connected_instagram_account', 'instagram_accounts{username,id,followed_by_count,media_count,profile_pic}', 'name', 'about']),
    #     'access_token': token,
    # })  # -> 186725698400085
    # resp.raise_for_status()
    # logging.info('API response: %r', resp.json())
