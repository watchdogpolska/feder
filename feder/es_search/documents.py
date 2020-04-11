from elasticsearch_dsl import Document, Keyword, Text


class LetterDocument(Document):
    title = Text(analyzer="snowball", required=True, fields={"raw": Keyword()})
    body = Text(analyzer="snowball", required=True)
    content = Text(analyzer="snowball", multi=True)

    class Index:
        name = "letter"
