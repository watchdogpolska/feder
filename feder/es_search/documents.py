from elasticsearch_dsl import Document, Keyword, Text


class LetterDocument(Document):
    title = Text(
        analyzer="snowball", required=True, fields={"raw": Keyword()}, term_vector="yes"
    )
    body = Text(analyzer="snowball", required=True, term_vector="yes")
    content = Text(analyzer="snowball", multi=True, term_vector="yes")
    letter_id = Text(multi=False)

    class Index:
        name = "letter"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
