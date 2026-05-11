from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    # increased maximum page size to allow export to CSV without pagination
    max_page_size = 10000
    page_size_query_param = "page_size"
