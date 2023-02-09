from rest_framework_csv.renderers import CSVStreamingRenderer
from django.contrib.sites.shortcuts import get_current_site


def get_full_url_for_context(path, context):
    scheme = (
        "{}://".format(context["request"].scheme)
        if "request" in context
        else "https://"
    )

    return "".join(
        [scheme, get_current_site(context.get("request", None)).domain, path]
    )

def get_clean_email(email: str) -> str:
    email = str(email)
    if ',' in email:
        email = email.split(',')[0]
    email = email[-99:]
    if '<' in email:
        email = email.split('<')[1]
    if '>' in email:
        email = email.split('>')[0]
    return email

class PaginatedCSVStreamingRenderer(CSVStreamingRenderer):
    def render(self, data, *args, **kwargs):
        """Copied form PaginatedCSVRenderer to support paginated results."""
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super().render(data, *args, **kwargs)
