from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import *
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class ReportViewSet(viewsets.ModelViewSet):

    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_permissions(self):

        if self.action in ['update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsOwnerAndDraftOrReadOnly()
            ]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def get_queryset(self):

        user = self.request.user

        queryset = Report.objects.all().order_by('-updated_at')

        tab = self.request.query_params.get('tab', None)

        if tab == 'my_reports':

            queryset = queryset.filter(
                reporter=user
            )

        elif tab == 'feed':

            queryset = queryset.filter(
                ~Q(status='DRAFT')
            )

        else:

            queryset = queryset.filter(
                ~Q(status='DRAFT') |
                Q(status='DRAFT', reporter=user)
            )

        return queryset
    
    def get_serializer_context(self):

        context = super().get_serializer_context()
        context['request'] = self.request

        return context