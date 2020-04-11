from .documents import LetterDocument
from tika import parser
from .settings import APACHE_TIKA_URL


def letter_serialize(letter):
    doc = LetterDocument()
    doc.title = letter.title
    doc.body = letter.body
    doc.meta.id = letter.id
    chunks = []
    for attachment in letter.attachment_set.all():
        text = parser.from_file(attachment.attachment.file.file, APACHE_TIKA_URL)[
            "content"
        ].strip()
        chunks.append(text)
    doc.content = chunks
    return doc
