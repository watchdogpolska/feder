from textwrap import TextWrapper
from html.parser import HTMLParser

BODY_REPLY_TPL = "\n\nProsimy o odpowiedź na adres {{EMAIL}}"
BODY_FOOTER_SEPERATOR = "\n\n--\n"


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


def html_to_text(html):
    parser = HTMLFilter()
    parser.feed(html)
    return parser.text


def text_email_wrapper(text):
    wrapper = TextWrapper()
    wrapper.subsequent_indent = "> "
    wrapper.initial_indent = "> "
    return "\n".join(wrapper.wrap(text))


def html_email_wrapper(html_quote):
    html = f"<blockquote>{html_quote}</blockquote>"
    return html


def normalize_msg_id(msg_id):
    if msg_id[0] == "<":
        msg_id = msg_id[1:]
    if msg_id[-1] == ">":
        msg_id = msg_id[:-1]
    return msg_id


def is_spam_check(email_object):
    return email_object["X-Spam-Flag"] == "YES"


def get_body_with_footer(body, footer):
    full_body = f"{body}{BODY_REPLY_TPL}"
    if footer.strip():
        full_body = f"{full_body}{BODY_FOOTER_SEPERATOR}{footer}"
    return full_body
