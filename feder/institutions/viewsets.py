import django_filters
from rest_framework import filters, viewsets

from .models import Email, Institution, Tag
from .serializers import EmailSerializer, InstitutionSerializer, TagSerializer
from teryt_tree.rest_framework_ext.viewsets import custom_area_filter


class InstitutionFilter(filters.FilterSet):
    jst = django_filters.CharFilter(action=custom_area_filter)

    class Meta:
        model = Institution
        fields = ['tags', 'jst']


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (Institution.objects.
                select_related('jst').
                prefetch_related('tags').
                with_accurate_email().
                all())
    serializer_class = InstitutionSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_class = InstitutionFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
