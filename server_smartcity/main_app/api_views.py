from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import *
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .permissions import IsOwnerAndDraftOrReadOnly

class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportViewSet(viewsets.ModelViewSet):
    """
    API untuk Citizen Portal.

    Aturan utama:
    - Citizen boleh membuat laporan melalui API.
    - Laporan baru otomatis berstatus DRAFT.
    - Admin tidak boleh membuat laporan melalui API.
    - DRAFT milik orang lain disembunyikan dengan 404.
    - Pemilik hanya boleh mengubah laporan saat status masih DRAFT.
    """

    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]

        if self.action in ['update', 'partial_update', 'destroy']:
            return [
                permissions.IsAuthenticated(),
                IsOwnerAndDraftOrReadOnly()
            ]

        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        tab = self.request.query_params.get('tab')

        queryset = Report.objects.all().order_by('-updated_at')

        if not user.is_authenticated:
            return queryset.exclude(status='DRAFT')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        if tab == 'feed':
            return queryset.exclude(status='DRAFT')

        return queryset.filter(
            Q(status__in=['REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED']) |
            Q(status='DRAFT', reporter=user)
        )

    def perform_create(self, serializer):
        user = self.request.user

        if getattr(user, 'is_admin', False):
            raise PermissionDenied(
                "Admin tidak diperbolehkan membuat laporan."
            )

        serializer.save(
            reporter=user,
            status='DRAFT'
        )

    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.reporter != self.request.user:
            raise PermissionDenied(
                "Anda tidak memiliki izin untuk mengubah laporan ini."
            )

        if instance.status != 'DRAFT':
            raise PermissionDenied(
                "Laporan yang sudah diajukan tidak dapat diubah."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.reporter != self.request.user:
            raise PermissionDenied(
                "Anda tidak memiliki izin untuk menghapus laporan ini."
            )

        if instance.status != 'DRAFT':
            raise PermissionDenied(
                "Laporan yang sudah diajukan tidak dapat dihapus."
            )

        instance.delete()

    def get_serializer_context(self):
        
        context = super().get_serializer_context()
        context['request'] = self.request
        
        return context