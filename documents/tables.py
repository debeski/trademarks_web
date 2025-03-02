import os
from django.utils.html import mark_safe
import django_tables2 as tables
from .models import Decree, Publication, Objection, FormPlus, Country, Government, ComType, DocType, DecreeCategory
from django.urls import reverse
# from django.utils.safestring import mark_safe
# from babel.dates import format_date


class GovernmentTable(tables.Table):
    edit = tables.Column(accessor='id', verbose_name='', empty_values=(), orderable=False)

    def __init__(self, *args, model_name=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.user = user
        # Check if the user has the permission and add the column accordingly
        if self.user and self.user.has_perm('documents.edit_sections'):
            self.base_columns['edit'].visible = True
        else:
            self.base_columns['edit'].visible = False
            
    class Meta:
        model = Government
        template_name = "django_tables2/bootstrap5.html"
        fields = ('name', 'edit')
        attrs = {'class': 'table table-hover table-responsive align-middle table-sm'}

    def render_edit(self, value):
        base_url = reverse("manage_sections")
        # Derive model name from the Meta.model class name
        model_name = self.Meta.model.__name__
        url = f"{base_url}?model={model_name}&id={value}"
        return mark_safe(f'<a href="{url}" class="btn btn-secondary">تعديل</a>')

class CountryTable(tables.Table):
    edit = tables.Column(accessor='id', verbose_name='', empty_values=(), orderable=False)

    def __init__(self, *args, model_name=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.user = user
        # Check if the user has the permission and add the column accordingly
        if self.user and self.user.has_perm('documents.edit_sections'):
            self.base_columns['edit'].visible = True
        else:
            self.base_columns['edit'].visible = False
            
    class Meta:
        model = Country
        template_name = "django_tables2/bootstrap5.html"
        fields = ('ar_name', 'en_name', 'edit')
        attrs = {'class': 'table table-hover table-responsive align-middle table-sm'}

    def render_edit(self, value):
        base_url = reverse("manage_sections")
        # Derive model name from the Meta.model class name
        model_name = self.Meta.model.__name__
        url = f"{base_url}?model={model_name}&id={value}"
        return mark_safe(f'<a href="{url}" class="btn btn-secondary">تعديل</a>')

class ComTypeTable(tables.Table):
    edit = tables.Column(accessor='id', verbose_name='', empty_values=(), orderable=False)

    def __init__(self, *args, model_name=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.user = user
        # Check if the user has the permission and add the column accordingly
        if self.user and self.user.has_perm('documents.edit_sections'):
            self.base_columns['edit'].visible = True
        else:
            self.base_columns['edit'].visible = False
            
    class Meta:
        model = ComType
        template_name = "django_tables2/bootstrap5.html"
        fields = ('name', 'edit')
        attrs = {'class': 'table table-hover table-responsive align-middle table-sm'}

    def render_edit(self, value):
        base_url = reverse("manage_sections")
        # Derive model name from the Meta.model class name
        model_name = self.Meta.model.__name__
        url = f"{base_url}?model={model_name}&id={value}"
        return mark_safe(f'<a href="{url}" class="btn btn-secondary">تعديل</a>')

class DocTypeTable(tables.Table):
    edit = tables.Column(accessor='id', verbose_name='', empty_values=(), orderable=False)

    def __init__(self, *args, model_name=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.user = user
        # Check if the user has the permission and add the column accordingly
        if self.user and self.user.has_perm('documents.edit_sections'):
            self.base_columns['edit'].visible = True
        else:
            self.base_columns['edit'].visible = False
            
    class Meta:
        model = DocType
        template_name = "django_tables2/bootstrap5.html"
        fields = ('name',)
        attrs = {'class': 'table table-hover table-responsive align-middle table-sm'}

    def render_edit(self, value):
        base_url = reverse("manage_sections")
        # Derive model name from the Meta.model class name
        model_name = self.Meta.model.__name__
        url = f"{base_url}?model={model_name}&id={value}"
        return mark_safe(f'<a href="{url}" class="btn btn-secondary">تعديل</a>')

class DecreeCategoryTable(tables.Table):
    edit = tables.Column(accessor='id', verbose_name='', empty_values=(), orderable=False)

    def __init__(self, *args, model_name=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.user = user
        # Check if the user has the permission and add the column accordingly
        if self.user and self.user.has_perm('documents.edit_sections'):
            self.base_columns['edit'].visible = True
        else:
            self.base_columns['edit'].visible = False
            
    class Meta:
        model = DecreeCategory
        template_name = "django_tables2/bootstrap5.html"
        fields = ('number', 'name')
        attrs = {'class': 'table table-hover table-responsive align-middle table-sm'}

    def render_edit(self, value):
        base_url = reverse("manage_sections")
        # Derive model name from the Meta.model class name
        model_name = self.Meta.model.__name__
        url = f"{base_url}?model={model_name}&id={value}"
        return mark_safe(f'<a href="{url}" class="btn btn-secondary">تعديل</a>')


class DecreeTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='partials/decree_actions.html',
        orderable=False,
        verbose_name=''
    )

    class Meta:
        model = Decree
        template_name = "django_tables2/bootstrap5.html"
        # List the fields you want to show in the table
        fields = ('number', 'date', 'status', 'applicant', 'company', 'country', 'ar_brand', 'en_brand', 'category__number', 'actions')
        attrs = {'class': 'table table-hover table-responsive align-middle'}
        
    # Custom method to render the Date
    def render_date(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''

class PublicationTable(tables.Table):
    # Define a custom column to display the image
    img_file = tables.Column(orderable=False, verbose_name="الصورة")

    # Define actions column for edit/delete
    actions = tables.TemplateColumn(
        template_name='partials/pub_actions.html',
        orderable=False,
        verbose_name=''
    )

    # Custom method to render the image
    def render_img_file(self, value):
        if value:
            # Assuming 'value' is a file field, you can generate the URL and return the image HTML
            return mark_safe(f'<img src="{value.url}" alt="Publication Image" class="img-thumbnail" style="height: 80px; width: auto;">')
        return ''
    
    # Custom method to render the Date
    def render_date_applied(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''
    
    def render_created_at(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''
    
    class Meta:
        model = Publication
        template_name = "django_tables2/bootstrap5.html"
        # List the fields you want to show in the table
        fields = ('number', 'decree', 'number_applied', 'applicant', 'country', 'address', 'date_applied', 'category', 'img_file', 'e_number', 'created_at', 'actions')
        attrs = {'class': 'table table-hover table-responsive align-middle'}


class ObjectionPubPickTable(tables.Table):
    # Define a custom column to display the image
    img_file = tables.Column(orderable=False, verbose_name="الصورة")

    # Custom method to render the image
    def render_img_file(self, value):
        if value:
            # Assuming 'value' is a file field, you can generate the URL and return the image HTML
            return mark_safe(f'<img src="{value.url}" alt="Publication Image" class="img-thumbnail" style="height: 80px; width: auto;">')
        return ''

    class Meta:
        model = Publication
        template_name = "django_tables2/bootstrap5.html"
        fields = ('number', 'decree', 'applicant', 'country', 'address', 'date_applied', 'category', 'img_file', 'e_number', 'created_at')
        attrs = {'class': 'table table-hover table-responsive align-middle', 'id': 'publication-table'}
        
    # Custom method to render the Date
    def render_date_applied(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''
    
    def render_created_at(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''
    
    # def render_number(self, value, record):
    #     """ Make the row clickable by embedding a hidden anchor inside the number field """
    #     url = reverse("add_pub_objection", kwargs={"document_id": record.id})
    #     return mark_safe(f'<a href="{url}" class="row-link">{value}</a>')

class ObjectionTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='partials/objection_actions.html',  # You will need to create this template for actions like view, edit, delete
        orderable=False,
        verbose_name=''
    )

    class Meta:
        model = Objection
        template_name = "django_tables2/bootstrap5.html"
        # List the fields you want to show in the table
        fields = ('number', 'pub', 'pub.number_applied', 'name', 'job', 'nationality', 'status', 'created_at', 'unique_code', 'actions')
        attrs = {'class': 'table table-hover table-responsive align-middle'}

    # Custom method to render the Date
    def render_created_at(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''


class FormPlusTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='partials/formplus_actions.html', 
        orderable=False, 
        verbose_name=''
    )

    class Meta:
        model = FormPlus
        template_name = "django_tables2/bootstrap5.html"
        fields = ('number', 'date', 'title', 'type', 'keywords')
        attrs = {'class': 'table table-hover table-responsive align-middle'}

    # Custom method to render the Date
    def render_date(self, value):
        # Format the date as desired (for example: dd-mm-yyyy)
        return value.strftime('%Y-%m-%d') if value else ''
