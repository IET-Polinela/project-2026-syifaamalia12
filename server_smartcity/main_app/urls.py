from django.urls import path
from .views import (
    HomeView,
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportUpdateStatusView,
    ReportSearchJsonView,
    ReportDetailJsonView,
)

urlpatterns = [
    # Landing Page
    path('', HomeView.as_view(), name='home_landing'),

    # Reports
    path('reports/', ReportListView.as_view(), name='report'),
    path('reports/detail/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),

    # CRUD
    path('reports/add/', ReportCreateView.as_view(), name='add_report'),
    path('reports/edit/<int:pk>/', ReportUpdateView.as_view(), name='edit_report'),
    path('reports/delete/<int:pk>/', ReportDeleteView.as_view(), name='delete_report'),

    # JSON for Live Search and Detail Modal
    path('reports/search/', ReportSearchJsonView.as_view(), name='report_search'),
    path('reports/<int:pk>/json/', ReportDetailJsonView.as_view(), name='report_detail_json'),

    # Workflow status
    path('reports/update-status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),
]