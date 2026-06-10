from django.contrib import admin
from django.urls import path, include
from usermanagement_24782064.views import CustomLoginView, CustomLogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usermanagement_24782064.api_views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
    path('', include('usermanagement_24782064.urls')),
    path('', include('dashboard_24782064.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),
    
    path('api/', include('main_app.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
]