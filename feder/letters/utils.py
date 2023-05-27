import re
from html.parser import HTMLParser
from textwrap import TextWrapper

from django.forms.widgets import TextInput

BODY_REPLY_TPL = "\n\nProsimy o odpowiedź na adres {{EMAIL}}"
BODY_FOOTER_SEPERATOR = "\n\n--\n"


class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.list_counter = 0
        self.list_type = ""

    def handle_data(self, data):
        self.text += data

    def handle_starttag(self, tag, attrs):
        if tag == "ul":
            self.list_type = "ul"
        elif tag == "ol":
            self.list_type = "ol"
        elif tag == "li":
            self.list_counter += 1
            self.text += self.get_list_prefix()
        elif tag == "br" or tag == "p":
            self.text += "\n"

    def handle_endtag(self, tag):
        if tag == "ul" or tag == "ol":
            self.list_counter = 0
            self.list_type = ""

    def get_list_prefix(self):
        if self.list_type == "ul":
            return "  - "
        elif self.list_type == "ol":
            return f"  {self.list_counter}. "

    def handle_entityref(self, name):
        if name == "nbsp":
            self.text += " "

    def handle_charref(self, name):
        if name == "160":
            self.text += " "


def html_to_text(html):
    parser = HTMLFilter()
    parser.feed(html)
    return parser.text


def text_email_wrapper(text):
    wrapper = TextWrapper(width=80, break_long_words=False)
    wrapper.subsequent_indent = "> "
    wrapper.initial_indent = "> "
    lines = text.split("\n")
    wrapped_text = ""
    for line in lines:
        wrapped_line = "\n".join(wrapper.wrap(line.strip()))
        if wrapped_line:
            wrapped_text += wrapped_line + "\n"
    return wrapped_text


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


class HtmlIframeWidget(TextInput):
    template_name = "letters/letter_html_iframe_widget.html"

    def get_context(self, name, value, attrs=None):
        context = super().get_context(name, value, attrs)
        context["widget"][
            "iframe_src"
        ] = value  # Assuming the widget value contains the iframe source URL
        return context


def is_formatted_html(text):
    is_html = bool(re.search(r"<[^<]+?>", text))
    return is_html


def text_to_html(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#39;")
    text = re.sub(r"  +|\t", lambda match: "&nbsp;" * len(match.group()), text)
    text = re.sub(r"(https?://\S+)", r'<a href="\1">\1</a>', text)
    text = text.replace("\n", "\n<br>")
    return "<p>" + text + "\n</p>"
