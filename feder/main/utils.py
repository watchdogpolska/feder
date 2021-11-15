from rest_framework_csv.renderers import CSVStreamingRenderer
from django.contrib.sites.shortcuts import get_current_site
import random
import string

from django.utils.timezone import now


def get_full_url_for_context(path, context):
    scheme = (
        "{}://".format(context["request"].scheme)
        if "request" in context
        else "https://"
    )

    return "".join(
        [scheme, get_current_site(context.get("request", None)).domain, path]
    )


class PaginatedCSVStreamingRenderer(CSVStreamingRenderer):
    def render(self, data, *args, **kwargs):
        """Copied form PaginatedCSVRenderer to support paginated results."""
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super().render(data, *args, **kwargs)


def prefix_gen(
    size=10, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase
):
    return "".join(random.choice(chars) for _ in range(size))


def date_random_path(prefix):
    def helper(instance, filename):
        return "{prefix}/{y}/{m}/{d}/{r}/{f}".format(
            prefix=prefix,
            y=now().year,
            m=now().month,
            d=now().day,
            r=prefix_gen(),
            f=filename[-320:],
        )

    return helper
