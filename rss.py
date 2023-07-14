"""
Renders a simple RSS item for a given list of items from Facebook or Instagram

https://farerskiekadry.pl/feed
https://www.w3schools.com/xml/xml_rss.asp

https://validator.w3.org/feed/

<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">

<channel>
  <title>W3Schools Home Page</title>
  <link>https://www.w3schools.com</link>
  <description>Free web building tutorials</description>
  <generator>vim</generator>
  <image>
    <url>https://www.w3schools.com/images/logo.gif</url>
    <title>W3Schools.com</title>
    <link>https://www.w3schools.com</link>
  </image>
  <item>
    <title>RSS Tutorial</title>
    <pubDate>Tue, 28 Mar 2023 21:37:58 +0000</pubDate>
    <link>https://www.w3schools.com/xml/xml_rss.asp</link>
    <description>New RSS tutorial on W3Schools</description>
  </item>
</channel>
</rss>
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TextIO
from xml.sax.saxutils import escape as escape_xml
from email.utils import formatdate

RSS_GENERATOR = 'py-facebook-feed'


@dataclass
class RssFeedItem:
    """
    An item that can be added to the RSS feed
    """
    title: str
    link: str
    description: str
    published: Optional[datetime]

    def __repr__(self) -> str:
        return f'{self.title} <{self.link}>'


class RssFeedWriter:
    """
    Class responsible for writing RSS files to a given text stream (can be a file)
    """
    def __init__(self, out: TextIO, title: str, link: str, description: Optional[str]):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.out = out
        self.title = title
        self.link = link
        self.description = description

    # https://book.pythontips.com/en/latest/context_managers.html#implementing-a-context-manager-as-a-class
    def __enter__(self):
        self.write_header()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write_footer()
        pass

    def _writelines(self, lines: list[str]):
        self.out.writelines([
            line + "\n"
            for line in lines
        ])

    def write_header(self):
        self._writelines([
            '<?xml version="1.0" encoding="UTF-8" ?>',
            '<rss version="2.0">',
            ' <channel>',
            f'  <title>{escape_xml(self.title)}</title>',
            f'  <link>{escape_xml(self.link)}</link>',
            f'  <description>{escape_xml(self.description)}</description>' if self.description else '',
            f'  <generator>{escape_xml(RSS_GENERATOR)}</generator>',
        ])

    def write_footer(self):
        self._writelines([
            ' </channel>',
            '</rss>'
        ])

    def add_item(self, item: RssFeedItem) -> None:
        """
        Adds the provided item to the RSS XML stream
        """
        # https://stackoverflow.com/a/3453266
        pub_date = float(item.published.strftime('%s')) if item.published else None

        # https://validator.w3.org/feed/docs/warning/MissingGuid.html
        # e.g. <guid isPermaLink="false">https://farerskiekadry.pl/?p=3541</guid>
        guid = item.link

        self.logger.info(f'add_item(): {repr(item)}')

        self._writelines([
            '  <item>',
            f'    <title>{escape_xml(item.title)}</title>',
            f'    <guid isPermaLink="false">{escape_xml(guid)}</guid>',
            f'    <link>{escape_xml(item.link)}</link>',
            f'    <description>{escape_xml(item.description)}</description>',
            f'    <pubDate>{escape_xml(formatdate(pub_date))}</pubDate>' if pub_date else '',
            '  </item>',
        ])
