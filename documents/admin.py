from django.contrib import admin
from .models import Country, Government, ComType, DocType, DecreeCategory, Decree, Publication, Objection, FormPlus
from .forms import CountryForm, GovernmentForm, ComTypeForm, DocTypeForm, DecreeCategoryForm, DecreeForm, PublicationForm, ObjectionForm, FormPlusForm

# Registering models with custom forms in the admin

class CountryAdmin(admin.ModelAdmin):
    form = CountryForm
    list_display = ['en_name', 'ar_name']


class GovernmentAdmin(admin.ModelAdmin):
    form = GovernmentForm
    list_display = ['name']


class ComTypeAdmin(admin.ModelAdmin):
    form = ComTypeForm
    list_display = ['name']


class DocTypeAdmin(admin.ModelAdmin):
    form = DocTypeForm
    list_display = ['name']


class DecreeCategoryAdmin(admin.ModelAdmin):
    form = DecreeCategoryForm
    list_display = ['number', 'name']


class DecreeAdmin(admin.ModelAdmin):
    form = DecreeForm
    list_display = ['number', 'date', 'status', 'applicant', 'company', 'country']
    search_fields = ['number', 'applicant', 'company']
    list_filter = ['status', 'category']


class PublicationAdmin(admin.ModelAdmin):
    form = PublicationForm
    list_display = ['number', 'decree_number', 'applicant', 'owner', 'year']
    search_fields = ['decree_number', 'applicant', 'owner']
    list_filter = ['year', 'category']


class ObjectionAdmin(admin.ModelAdmin):
    form = ObjectionForm
    list_display = ['number', 'name', 'job', 'nationality', 'is_paid']
    search_fields = ['number', 'name', 'com_name']
    list_filter = ['is_paid']


class FormPlusAdmin(admin.ModelAdmin):
    form = FormPlusForm
    list_display = ['number', 'date', 'title']
    search_fields = ['number', 'date', 'title']

# Registering the models with their corresponding admin classes
admin.site.register(Country, CountryAdmin)
admin.site.register(Government, GovernmentAdmin)
admin.site.register(ComType, ComTypeAdmin)
admin.site.register(DocType, DocTypeAdmin)
admin.site.register(DecreeCategory, DecreeCategoryAdmin)
admin.site.register(Decree, DecreeAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Objection, ObjectionAdmin)
admin.site.register(FormPlus, FormPlusAdmin)