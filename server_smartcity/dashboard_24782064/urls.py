from django.urls import path
from .views import DashboardView, DashboardDataView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/data/', DashboardDataView.as_view(), name='dashboard_data'),
    path('dashboard/api/data/', DashboardDataView.as_view(), name='dashboard_api_data'),
]
