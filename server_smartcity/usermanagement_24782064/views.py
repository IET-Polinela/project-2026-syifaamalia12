from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CitizenRegisterForm
from django.contrib.auth.views import LoginView, LogoutView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, "Login berhasil")
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_admin:
            return '/admin/'
        return '/'
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Logout berhasil")
        return super().dispatch(request, *args, **kwargs)
    
class RegisterView(CreateView):
    form_class = CitizenRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Registrasi berhasil. Silakan login.')
        return super().form_valid(form)