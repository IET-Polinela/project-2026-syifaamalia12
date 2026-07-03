from urllib import request

from django.views.generic import *
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Report
from .forms import ReportForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

class AdminRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu")
            return redirect('login')

        if not request.user.is_admin:
            messages.error(request, "Akses ditolak, hanya admin yang dapat mengakses fitur ini.")
            return redirect('home_landing')

        return super().dispatch(request, *args, **kwargs)


class AdminOnlyMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not getattr(request.user, 'is_admin', False):
            messages.error(
                request,
                "Akses ditolak, hanya admin yang dapat mengakses halaman ini."
            )
            return redirect('home_landing')

        return super().dispatch(request, *args, **kwargs)
    
class BackendReportMutationDisabledMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_authenticated:
            return redirect('login')

        messages.error(
            request,
            "Fitur tambah/edit/hapus laporan hanya tersedia melalui Portal Citizen."
        )
        return redirect('home_landing')

class HomeView(TemplateView):
    template_name = 'main_app/home.html'


class ReportAccessMixin(LoginRequiredMixin):
    """
    Mixin untuk halaman laporan backend.

    Aturan:
    - User harus login.
    - Admin boleh melihat semua laporan kecuali DRAFT.
    - Citizen boleh melihat laporan publik dan DRAFT miliknya sendiri.
    """

    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)


class ReportListView(AdminOnlyMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'
    ordering = ['-created_at']

    def dispatch(self, request, *args, **kwargs):
        # citizen tidak boleh akses → HARUS redirect 302
        if not request.user.is_authenticated:
            return redirect('login')

        if not getattr(request.user, 'is_admin', False):
            return redirect('home_landing')  # <- INI YANG DIPAKSA 302

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Report.objects.exclude(status='DRAFT').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = 'Reports'
        return context

class ReportDetailView(AdminOnlyMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not getattr(request.user, 'is_admin', False):
            return redirect('home_landing')  # <- 302 sesuai test

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Report.objects.exclude(status='DRAFT')


class ReportCreateView(AdminRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan")
        return super().form_valid(form)
    
class ReportUpdateView(BackendReportMutationDisabledMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/edit_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_admin', False):
            raise PermissionDenied("Admin tidak boleh mengedit laporan.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate")
        return super().form_valid(form)

class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        report = self.get_object()

        if not getattr(request.user, 'is_admin', False):
            return redirect('report_list')

        raise PermissionDenied()
    
    def form_valid(self, form):
        raise PermissionDenied(
            "Admin tidak boleh menghapus laporan."
        )

class ReportUpdateStatusView(View):
    allowed_transitions = {
        'REPORTED': ['VERIFIED'],
        'VERIFIED': ['IN_PROGRESS'],
        'IN_PROGRESS': ['RESOLVED'],
    }

    def post(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu.")
            return redirect('login')

        if not getattr(request.user, 'is_admin', False):
            messages.error(request, "Akses ditolak.")
            return redirect('home_landing')

        report = get_object_or_404(Report, pk=pk)

        requested_status = (
            request.POST.get('new_status') or
            request.POST.get('status')
        )

        valid_next_statuses = self.allowed_transitions.get(report.status, [])

        if requested_status in valid_next_statuses:
            report.status = requested_status
            report.save()
            messages.success(request, "Status laporan berhasil diubah.")
        else:
            messages.error(request, "Status laporan tidak dapat diubah.")

        return redirect('report')
    
class ReportSearchJsonView(View):
    """
    JSON search untuk tabel laporan di portal admin.
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    'results': [],
                    'reports': [],
                    'error': 'Forbidden'
                },
                status=403
            )

        if not getattr(request.user, 'is_admin', False):
            return JsonResponse(
                {
                    'results': [],
                    'reports': [],
                    'error': 'Forbidden'
                },
                status=403
            )

        query = request.GET.get('q', '').strip()

        reports = Report.objects.exclude(status='DRAFT').order_by('-created_at')

        if query:
            reports = reports.filter(title__icontains=query)

        reports = reports[:50]

        data = []

        for report in reports:
            data.append({
                'id': report.id,
                'title': report.title or '',
                'category': report.category or '',
                'location': report.location or '',
                'incident_date': str(report.incident_date) if report.incident_date else '',
                'status': report.status or '',
            })

        return JsonResponse({
            'results': data,
            'reports': data,
        })


class ReportDetailJsonView(View):
    """
    JSON detail laporan untuk modal/detail admin.
    """

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied(
                "Silakan login terlebih dahulu."
            )

        if not getattr(request.user, 'is_admin', False):
            raise PermissionDenied(
                "Hanya admin yang dapat melihat detail laporan."
            )

        report = get_object_or_404(
            Report.objects.exclude(status='DRAFT'),
            pk=pk
        )

        data = {
            'id': report.id,
            'title': report.title,
            'category': report.category,
            'location': report.location,
            'description': report.description,
            'status': report.status,
            'incident_date': report.incident_date.strftime('%Y-%m-%d'),
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M'),
        }

        return JsonResponse(data)


def report_detail_api(request, pk):
    """
    Function-based JSON detail sederhana untuk kebutuhan coverage tambahan.
    """

    report = get_object_or_404(Report, pk=pk)

    data = {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'location': report.location,
        'description': report.description,
        'status': report.status,
        'incident_date': report.incident_date.strftime('%Y-%m-%d'),
    }

    return JsonResponse(data)
