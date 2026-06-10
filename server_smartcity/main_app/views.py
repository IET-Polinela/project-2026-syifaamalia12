from django.views.generic import *
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Report
from .forms import ReportForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

class AdminRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu")
            return redirect('login')

        if not request.user.is_admin:
            messages.error(request, "Akses ditolak, hanya admin yang dapat mengakses fitur ini.")
            return redirect('report')

        return super().dispatch(request, *args, **kwargs)
    
class HomeView(TemplateView):
    template_name = 'main_app/home_landing.html'


class ReportListView(ListView):
    model = Report
    template_name = 'main_app/home.html'
    context_object_name = 'reports'
    ordering = ['-created_at']


class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'


class ReportCreateView(AdminRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil ditambahkan")
        return super().form_valid(form)

class ReportUpdateView(AdminRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'main_app/edit_report.html'
    success_url = reverse_lazy('report')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil diupdate")
        return super().form_valid(form)


class ReportDeleteView(AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/delete_report.html'
    success_url = reverse_lazy('report')

    def form_valid(self, form):
        messages.success(self.request, "Laporan berhasil dihapus")
        return super().form_valid(form)


class ReportUpdateStatusView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Silakan login terlebih dahulu")
            return redirect('login')

        if not request.user.is_admin:
            messages.error(request, "Akses Ditolak")
            return redirect('report')

        report = get_object_or_404(Report, pk=pk)

        flow = {
            'REPORTED': 'VERIFIED',
            'VERIFIED': 'IN_PROGRESS',
            'IN_PROGRESS': 'RESOLVED',
        }

        if report.status in flow:
            report.status = flow[report.status]
            report.save()
            messages.success(request, "Status berhasil diubah")
        else:
            messages.error(request, "Status tidak dapat diubah")

        return redirect('report')
    
class ReportSearchJsonView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        reports = Report.objects.all().order_by('-created_at')

        if query:
            reports = reports.filter(title__icontains=query)

        data = list(
            reports.values(
                'id',
                'title',
                'category',
                'location',
                'incident_date',
                'status'
            )
        )

        return JsonResponse({'reports': data})


class ReportDetailJsonView(View):
    def get(self, request, pk, *args, **kwargs):
        report = get_object_or_404(Report, pk=pk)

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