from rest_framework import viewsets

from .models import Email, Institution, Tag
from .serializers import EmailSerializer, InstitutionSerializer, TagSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = (Institution.objects.
                select_related('jst').
                prefetch_related('tags').
                with_accurate_email().
                all())
    serializer_class = InstitutionSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
