import logging
import time

from requests.exceptions import ConnectionError
from tika import parser

from .documents import LetterDocument
from .settings import APACHE_TIKA_URL

MAX_RETRIES = 5
WAIT_TIME = 30

logger = logging.getLogger(__name__)


def letter_serialize(letter):
    doc = LetterDocument()
    doc.title = letter.title
    doc.body = letter.body
    doc.letter_id = letter.pk
    for attachment in letter.attachment_set.all():
        for i in range(MAX_RETRIES):
            try:
                if attachment.attachment.file.file.closed:
                    with attachment.attachment.file.file.open(mode="rb") as f:
                        text = parser.from_buffer(f, APACHE_TIKA_URL)["content"]
                    break
                else:
                    text = parser.from_file(
                        attachment.attachment.file.file, APACHE_TIKA_URL
                    )["content"]
                    break
            except ConnectionError as e:
                logger.error(f"Error: {e}")
                if i == MAX_RETRIES - 1:
                    logger.error(
                        f"Max retries exceeded. Skipping attachment {attachment.pk}"
                    )
                    text = ""
                    break
                logger.info(f"Retrying in {WAIT_TIME} seconds...")
                time.sleep(WAIT_TIME)
            except ValueError as e:
                logger.error(f"Error: {e}")
                logger.error(f"Skipping attachment {attachment.pk}")
                text = ""
                break
            except Exception as e:
                logger.error(f"Error: {e}, ")
                logger.error(f"Skipping attachment {attachment.pk}")
                text = ""
                break
        if text:
            doc.content.append(text.strip())
    # print("title", doc.title)
    # print("body", doc.body)
    # print("content", doc.content)
    return doc
