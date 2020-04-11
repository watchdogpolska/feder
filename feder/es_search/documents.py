from elasticsearch_dsl import Document, InnerDoc, Nested, Date, Keyword, Text


class LetterDocument(Document):
    title = Text(analyzer="snowball", fields={"raw": Keyword()})
    body = Text(analyzer="snowball")
    content = Text(analyzer="snowball")

    class Index:
        name = "letter"
