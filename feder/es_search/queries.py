from elasticsearch_dsl import Search, Index
from elasticsearch_dsl.query import MultiMatch, Match, Q, MoreLikeThis
from elasticsearch_dsl.connections import get_connection, connections
from .documents import LetterDocument


def serialize_document(doc):
    return {
        "_id": doc.__dict__["meta"]["id"],
        "_index": doc.__dict__["meta"]["index"],
    }


def search_keywords(query):
    q = MultiMatch(query=query, fields=["title", "body", "content"])
    return LetterDocument.search().query(q).execute()


def more_like_this(doc):
    like = serialize_document(doc)
    q = MoreLikeThis(like=like, fields=["title", "body"],)
    query = LetterDocument.search().query(q)
    # print(query.to_dict())
    return query.execute()
