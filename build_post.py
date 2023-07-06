# Builds the post combining a few Facebook feed post filtered from farerskie_kadry.ndjson file
#
# Writes the html to the post.html file
import json
import logging
import re
from typing import TextIO, Iterator


def parse_feed_from_file(stream_in: TextIO) -> Iterator[dict]:
    logger = logging.getLogger('parse_feed_from_file')

    for line in stream_in:
        row = json.loads(line)
        logger.debug(f'Post: {row["message"][0:64]}')

        if '2018-07-18' <= row['created_time'] <= '2018-08-28':
            if 'FarerskiDziennikZPodróży' in row['message']:
                yield row


def sanitize_message(message: str) -> str:
    message = message.replace('#FarerskiDziennikZPodróży', '')
    return message.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open('post.html', 'wt') as output:
        with open('farerskie_kadry.ndjson', 'rt') as fp:
            posts = list(parse_feed_from_file(stream_in=fp))

            # make the posts to be in chronological order
            posts.reverse()

            curl = []

            for idx, post in enumerate(posts):
                # https://farerskiekadry.pl/wp-content/uploads/2023/07/Dziennik-z-podrozy-2018_01.jpg
                if '/fb.png' not in post["full_picture"]:
                    curl.append(f'curl \'{post["full_picture"]}\' > /tmp/Dziennik-z-podrozy-2018_{str(idx+1).zfill(2)}.jpg')

                    image = f'https://farerskiekadry.pl/wp-content/uploads/2023/07/Dziennik-z-podrozy-2018_{str(idx+1).zfill(2)}.jpg'
                else:
                    image = None

                # post-process the message
                message = sanitize_message(post['message'])

                # find the "Dzień N" header
                day_header = re.match(r'(Dzień [\d i]+.)', message)  # ; print([day_header, message])

                message = message.replace(day_header.group(1), '') if day_header else message
                day_header = day_header.group(1) if day_header else 'Dzień N'

                message = re.sub(r'\n+', '</p><p>', message)

                # write HTML
                output.write(f"<h2 style='clear: both'>{day_header.rstrip('.')}</h2>\n")

                image_align = 'left' if idx % 2 else 'right'
                published = post['created_time'][0:10]

                published = f'{published[8:10].lstrip("0")} {"lipca" if published[5:7] == "07" else "sierpnia"} {published[0:4]}'
                # print([published, post['created_time'][0:10]])

                output.write(
                f"""
                <div class="wp-block" data-align="{image_align}">
                <figure tabindex="0" class="block-editor-block-list__block is-resized is-multi-selected wp-block-image"
                <div class="components-resizable-box__container" style="position: relative; user-select: auto; width: 542px; height: 360px;">
                <img style="max-width: 542px; max-height: 360px;" src="{image}" alt="Dziennik z podróży - {day_header}">
                </div>
                </figure></div>
                """
                ) if image else None
                output.write(f"<p>{message}</p>\n")
                output.write(f"<p><small><a href='{post['permalink_url']}'>Notka z {published}</a></small></p>\n")

                """
                print(
                    "\n\n-------\n",
                    sanitize_message(post['message']),
                    # post['full_picture'],
                    '\n',
                    image,
                    post['permalink_url']
                )
                """

        # now, print out some pictures download instructions
        # print("\n\ncURL instruction:\n" + "\n".join(curl))
