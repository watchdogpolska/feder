from textwrap import TextWrapper


def email_wrapper(text):
    wrapper = TextWrapper()
    wrapper.subsequent_indent = '> '
    wrapper.initial_indent = '> '
    return "\n".join(wrapper.wrap(text))
