from .documents import LetterDocument
from tika import parser
from .settings import APACHE_TIKA_URL


def letter_serialize(letter):
    doc = LetterDocument()
    doc.title = letter.title
    doc.body = letter.body
    doc.letter_id = letter.pk
    for attachment in letter.attachment_set.all():
        text = parser.from_file(attachment.attachment.file.file, APACHE_TIKA_URL)[
            "content"
        ]
        if text:
            doc.content.append(text.strip())
    # print("title", doc.title)
    # print("body", doc.body)
    # print("content", doc.content)
    return doc
