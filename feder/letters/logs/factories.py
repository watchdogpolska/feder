from collections import OrderedDict

import factory.fuzzy
import factory

from feder.letters.logs.models import EmailLog, STATUS


def get_emaillabs_row(sender_from="sprawa@example.com", **values):
    data = {
        "account": "1.siecobywatelska.smtp",
        "created_at": None,
        "from": sender_from,
        "id": "59916eb9e4c40955c53e98f1",
        "injected_time": "2017-08-14 11:31:12",
        "message_id": "20170814093112.39609.36709@localhost",
        "postfix_id": ["3xW9N049HSz6Q5qN", "3xW9N03F3TzBTXW1"],
        "subject": "Lorem Ipsum",
        "tags": [],
        "to": "gov@example.com",
        "tracking": [],
        "uid": "7488a57d6fa8654b84e413b9adfd2acb",
        "updated_at": None,
        "vps": "smtp2-87",
    }
    data.update(values)
    return data


class EmailLogFactory(factory.django.DjangoModelFactory):
    status = factory.Iterator(OrderedDict(STATUS).keys())
    case = factory.SubFactory("feder.cases.factories.CaseFactory")
    email_id = factory.Sequence("emaillog-email_id-{}".format)

    @factory.lazy_attribute
    def to(self):
        return self.case.email

    class Meta:
        model = "logs.EmailLog"


class LogRecordFactory(factory.django.DjangoModelFactory):
    email = factory.SubFactory("feder.letters.logs.factories.EmailLogFactory")

    @factory.lazy_attribute
    def data(self):
        return get_emaillabs_row(to=self.email.to, id=self.email.email_id)

    class Meta:
        model = "logs.LogRecord"
