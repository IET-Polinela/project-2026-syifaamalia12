from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import *

class ReportViewSet(viewsets.ModelViewSet):

    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_permissions(self):

        if self.action in ['update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsOwnerAndDraftOrReadOnly()
            ]

        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):

        serializer.save(reporter=self.request.user)