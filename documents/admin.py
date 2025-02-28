from django.contrib import admin
from .models import Decree, Publication, Objection
# Register your models here.


# admin.site.register(Decree)


@admin.register(Decree)
class ImportRecordAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'status', 'applicant', 'company', 'country', 'ar_brand', 'en_brand', 'category', 'created_at', 'deleted_at')
    list_filter = ('date', 'status', 'country', 'date_applied')
    search_fields = ('number', 'applicant', 'company', 'ar_brand', 'en_brand')
    ordering = ('number', 'applicant', 'company', 'date', 'date_applied', 'created_at', 'deleted_at')
    
    
@admin.register(Publication)
class ImportRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'number', 'e_number', 'created_at', 'decree', 'status', 'applicant', 'owner', 'country', 'ar_brand', 'en_brand', 'category', 'deleted_at')
    list_filter = ('status', 'country', 'date_applied')
    search_fields = ('number', 'applicant', 'owner', 'ar_brand', 'en_brand')
    ordering = ('year', 'number', 'applicant', 'owner', 'created_at', 'date_applied', 'deleted_at')