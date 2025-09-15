# py-facebook-feed
[![Update RSS feeds](https://github.com/macbre/farerskie-kadry-feed/actions/workflows/update-rss.yml/badge.svg)](https://github.com/macbre/farerskie-kadry-feed/actions/workflows/update-rss.yml)

## Install

```
virtualenv env -ppython3
. env/bin/activate
pip install -r requirements.txt
python main.py
```

## Access token

Make sure that `FB_TOKEN` env variable is set to the proper access token.

* https://developers.facebook.com/tools/accesstoken/
* https://developers.facebook.com/tools/debug/accesstoken/
* https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/#long-lived-page-token 

For iterating over Instagram feed you need the FB access token with the `instagram_basic` right.
