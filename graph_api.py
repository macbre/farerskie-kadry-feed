# Provides a generic iterator over paged feeds from https://graph.facebook.com API,
# handling both Facebook and Instagram.
import dataclasses
import logging
from datetime import datetime
from time import strptime
from typing import Iterable

from requests import Session

# keep the HTTP session
http = Session()
http.headers['user-agent'] = 'py-facebook-feed'


@dataclasses.dataclass
class ResponseEntity:
    """
    Generic entity dataclass for Facebook posts and Instagram media
    """
    message: str
    permalink_url: str
    full_picture: str
    created_time: datetime

    def __repr__(self) -> str:
        return f'{self.message[0:96]}... ({self.created_time.isoformat()}) <{self.permalink_url}>'

    def dict(self) -> dict:
        return {
            k: str(v) if v is not None else None
            for k, v in dataclasses.asdict(self).items()
        }


def make_request(endpoint: str, req_params: dict) -> dict:
    logger = logging.getLogger('make_request')

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

    return resp.json()


def iterate_api_responses(endpoint: str, req_params: dict) -> Iterable[dict]:
    """
    Yields data items for all paged response of the given endpoint
    """
    logger = logging.getLogger('iterate_api_responses')
    logger.info(f'HTTP request to {endpoint}')

    items_counter = 0

    while True:
        resp_json = make_request(endpoint, req_params)
        logger.debug('API response: %r', resp_json)
        logger.debug('API paging: %r', resp_json.get('paging'))

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


# e.g. 2023-02-27T14:31:39+0000
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


def created_time_field_to_datetime(created_time: str) -> datetime:
    """
    Converts strings with times (as returned by Facebook's API) to Python's datatime

    e.g.  2023-02-27T14:31:39+0000
    """
    return datetime(*(strptime(created_time, DATE_FORMAT)[0:6]))
