from django.urls import path
from .views import (
    HomeView,
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportUpdateStatusView
)

urlpatterns = [
    # Landing Page (Home)
    path('', HomeView.as_view(), name='home_landing'),

    # Reports (Daftar laporan)
    path('reports/', ReportListView.as_view(), name='report'),

    # CRUD
    path('add/', ReportCreateView.as_view(), name='add_report'),
    path('edit/<int:pk>/', ReportUpdateView.as_view(), name='edit_report'),
    path('delete/<int:pk>/', ReportDeleteView.as_view(), name='delete_report'),
    path('detail/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),

    # Workflow status
    path('update-status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),
]