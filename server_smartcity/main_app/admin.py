from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'location',
        'status',
        'reporter',
        'incident_date',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'status',
        'category',
        'incident_date',
        'created_at',
    )
    search_fields = (
        'title',
        'description',
        'location',
        'category',
        'reporter__username',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    ordering = (
        '-updated_at',
    )