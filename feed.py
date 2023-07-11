# Provides a generic iterator over paged feeds from https://graph.facebook.com API,
# handling both Facebook and Instagram.
import logging
from typing import Iterable

from requests import Session


def iterate_api_responses(endpoint: str, req_params: dict) -> Iterable[dict]:
    """
    Yields data items for all paged response of the given endpoint
    """
    logger = logging.getLogger('iterate_api_responses')
    logger.info(f'HTTP request to {endpoint}')

    http = Session()
    http.headers['user-agent'] = 'py-facebook-feed'

    items_counter = 0

    while True:
        try:
            resp = http.get(f'https://graph.facebook.com/{endpoint.lstrip("/")}', params=req_params)
        except:
            logger.error(f'API request to {endpoint} failed', exc_info=True)
            raise

        try:
            resp.raise_for_status()
        except:
            logger.error('API response: %s', resp.text, exc_info=True)
            raise

        resp_json = resp.json()
        logger.debug('API response: %r', resp_json)
        logger.info('API paging: %r', resp_json.get('paging'))

        for item in resp_json.get('data', []):
            items_counter += 1
            yield item

        try:
            req_params['after'] = resp_json['paging']['cursors']['after']
            logger.debug('API next page (after) cursor: %r', req_params['after'])
        except KeyError:
            # no more pages to iterate over
            logger.info(f'API returned {items_counter} items')
            return
