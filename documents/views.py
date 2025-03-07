# Fundemental imports
#####################
import logging
from django.contrib import messages
import os
from django.utils import timezone
from django.views import View
from django.apps import apps
from django.core.cache import cache
import importlib
import datetime
from django.utils.safestring import mark_safe
import qrcode
import base64
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# from googletrans import Translator

# Helping imports
#################
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import FileResponse, JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.module_loading import import_string

# JSON imports
##############
import json
import mimetypes
import zipfile
from io import BytesIO

# Project imports
#################
from .models import Decree, DecreeStatus, Publication, PublicationStatus, Objection, ObjectionStatus, FormPlus, Country, Government, ComType, DocType, DecreeCategory
from .genpdf import pub_pdf, obj_pdf, pub_final_pdf

# Design imports
################
from django_tables2 import RequestConfig
from django.db.models import Q
import pandas as pd
import plotly.express as px

#####################################################################
# low-level Logging initialization
logger = logging.getLogger('documents')
from users.models import  UserActivityLog
from users.signals import get_client_ip

# low-level Logging Function
def log_action(action, model, object_id=None):
    timestamp = timezone.now()
    message = f"{timestamp} - Performed {action} on {model.__name__} (ID: {object_id})"
    logger.info(message)

# Function to recognize superuser
def is_superuser(user):
    return user.is_superuser 

# Function that extracts model name from a string
def get_class_from_string(class_path):
    """Dynamically imports and returns a class from a string path."""
    return import_string(class_path)

# Function for generating a QR code for a 13 digit sequence
def generate_obj_qr(sequence):
    # Ensure the input is exactly 13 digits
    if not sequence.isdigit() or len(sequence) != 13:
        raise ValueError("Invalid sequence")

    # Generate QR code
    qr = qrcode.make(sequence)

    # Save QR to an in-memory buffer
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

# Function for generating a QR code for a publication url
def generate_pub_qr(pub_id):
    # Define the base URL (you can modify it to be dynamic later)
    base_url = "https://localhost:9430/publications/detail/"

    # Dynamically set the publication ID (for example, publication with ID 3)
    publication_id = pub_id
    full_url = f"{base_url}{publication_id}/"

    # Generate QR code
    qr = qrcode.make(full_url)

    # Save QR to an in-memory buffer
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

# Function for converting a buffer to base64 for PDF rendering
def buffer_to_base64(buffer):
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


#####################################################################
# Class Function for fetching related Decrees based on a year
class DecreeAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        decree_id = request.GET.get('id')  # Fetch using ID
        query = request.GET.get('q', '')
        year = request.GET.get('year', '')

        if decree_id:  # Fetch single decree by ID
            try:
                decree = Decree.objects.get(id=decree_id)
                return JsonResponse({
                    'id': decree.id,
                    'number': decree.number,
                    'date': decree.date.strftime("%Y-%m-%d") if decree.date else "",
                    'owner': decree.applicant,
                    'country': decree.country.id,
                    'date_applied': decree.date_applied.strftime("%Y-%m-%d") if decree.date_applied else "",
                    'number_applied': decree.number_applied if decree.number_applied else "",
                    'ar_brand': decree.ar_brand,
                    'en_brand': decree.en_brand,
                    'category': decree.category.id,
                })
            except Decree.DoesNotExist:
                return JsonResponse({}, status=404)

        qs = Decree.objects.filter(status=1).exclude(deleted_at__isnull=False)
        if year:
            qs = qs.filter(date__year=year)
        if query:
            qs = qs.filter(number__startswith=query)

        results = [
            {
                'id': decree.id,
                'number': decree.number,
                'date': decree.date.strftime("%Y-%m-%d") if decree.date else "",
            }
            for decree in qs
        ]
        return JsonResponse(results, safe=False)


# Class Function for fetching related Publications based on a year
class PublicationAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        year = request.GET.get('year', '')
        qs = Publication.objects.filter(status=1, deleted_at__isnull=True)
        if year:
            qs = qs.filter(created_at__year=year)
        if query:
            qs = qs.filter(number__startswith=query)

        # Build a list of dictionaries for each publication
        results = [
            {
                'year': pub.year if pub.year else "",
                'number': pub.number,
                'id': pub.id,
                'decree': pub.decree.number if pub.decree else "",
                'created_at': pub.created_at.strftime("%Y-%m-%d") if pub.created_at else "",
                'applicant': pub.applicant,
                'owner': pub.owner,
                'country': pub.country.ar_name,
                'address': pub.address,
                'date_applied': pub.date_applied.strftime("%Y-%m-%d") if pub.date_applied else "",
                'number_applied': pub.number_applied if pub.number_applied else "",
                'ar_brand': pub.ar_brand,
                'en_brand': pub.en_brand,
                'category': pub.category.number,
                'img_file': pub.img_file.url if pub.img_file else "",
            }
            for pub in qs
        ]

        return JsonResponse(results, safe=False)


# Function for Chart generation 
def create_chart(models, start_year=2012, end_year=2025):
    """
    Generates a Plotly bar chart for document counts per year across multiple models.
    Uses caching to improve performance.
        
    :param models: List of Django models to include in the chart.
    :param start_year: Start year for filtering (default: 2012).
    :param end_year: End year for filtering (default: 2025).
    :return: HTML representation of the Plotly chart.
    """
    
    # Construct a unique cache key based on input parameters
    cache_key = f"chart_{start_year}_{end_year}_" + "_".join([model.__name__ for model in models])
    cached_chart = cache.get(cache_key)

    # Return the cached chart if available
    if cached_chart:
        return cached_chart  
    
    years = range(start_year, end_year + 1)
    data = []

    # Collect data from each model
    for model in models:
        model_name = model._meta.verbose_name  # Use Django's verbose_name for readability
        year_field = None

        # Determine the correct field to filter by year
        if hasattr(model, 'year'):  # Model with explicit 'year' field
            year_field = 'year'
        elif hasattr(model, 'created_at'):  # Model using 'created_at'
            year_field = 'created_at__year'
        elif hasattr(model, 'date'):  # Model using 'date'
            year_field = 'date__year'

        if year_field:
            for year in years:
                # Get the count of documents for the given year
                count = model.objects.filter(**{year_field: year}, deleted_at__isnull=True).count() or 0
                data.append({'Year': year, 'Count': count, 'Model': model_name})

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Create the bar chart
    fig = px.bar(
        df, x='Year', y='Count', color='Model', barmode='group',
        title='عدد الوثائق حسب السنة',
        labels={'Model': 'النوع', 'Year': 'السنة', 'Count': 'عدد الوثائق'},
        text='Count',
        hover_data={'Model': False},
    )
    
    # Update layout with hover label alignment for RTL
    fig.update_layout(
        height=340,
        title_x=0.5,
        xaxis_title='',
        yaxis_title='عدد الوثائق',
        showlegend=False,
        autosize=True,
        margin=dict(l=40, r=20, t=40, b=0),
        font=dict(family='Shabwa, sans-serif', size=16),
        hoverlabel=dict(
            font=dict(
                family="Shabwa, sans-serif",
                size=14,
                color="white"  # Text color
            ),
            bgcolor="rgba(11, 27, 99, 0.9)"  # Background color
        )
    )

    # Convert figure to HTML representation
    chart_html = fig.to_html(full_html=False)
    # Store the chart in the cache for 1 hour (3600 seconds)
    cache.set(cache_key, chart_html, timeout=3600)
    return chart_html


# Html & Chart Rendering Functions on index page
def index(request):
    # Generate the chart HTML
    chart_html = create_chart([Publication, Decree, Objection])

    decree = Decree.objects.filter(deleted_at__isnull=True)
    decree_accept = decree.filter(status=1).count()
    decree_reject = decree.filter(status=2).count()

    
    # Get the total number of publications with status 'final'
    publications = Publication.objects.filter(deleted_at__isnull=True)
    pub_initial = publications.filter(status=1).count()
    pub_conflict = publications.filter(status=2).count()
    pub_final = publications.filter(status=3).count()

    # Get the total number of objections with status 'pending'
    objections = Objection.objects.filter(deleted_at__isnull=True)
    obj_pending = objections.filter(Q(status=1) | Q(status=2)).count()
    obj_paid = objections.filter(status=3).count()
    obj_accept = objections.filter(status=4).count()

    # Pass the values to the template context
    context = {
        'chart_html': chart_html,
        'decree_accept': decree_accept,
        'decree_reject': decree_reject,
        'decree_total': decree.count(),
        'pub_initial': pub_initial,
        'pub_conflict': pub_conflict,
        'pub_final': pub_final,
        'obj_pending': obj_pending,
        'obj_paid': obj_paid,
        'obj_accept': obj_accept,
        'version': settings.VERSION,
    }

    return render(request, 'index.html', context)


# About Us View
# def readme_view(request):
#     readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.MD')
    
#     try:
#         with open(readme_path, "r", encoding="utf-8") as f:
#             content = f.read()
        
#         # Translate to Arabic
#         translator = Translator()
#         translated_content = translator.translate(content, dest="ar").text

#     except FileNotFoundError:
#         translated_content = "ملف README.MD غير موجود."

#     return render(request, "about.html", {"content": translated_content})



# Main view, and CRUD function for section models
def core_models_view(request):
    # Read the GET parameter, defaulting to 'Country'
    model_param = request.GET.get('model', 'Country')
    
    # Mapping of model name (as string) to the actual model class
    models_map = {
        'Country': Country,
        'Government': Government,
        'ComType': ComType,
        'DocType': DocType,
        'DecreeCategory': DecreeCategory,
    }
    
    # Fallback to default if an invalid model is provided
    if model_param not in models_map:
        model_param = 'Country'
    
    selected_model = models_map[model_param]
    
    # Prepare models list with verbose names
    models_list = [
        {'name': key, 'ar_names': model._meta.verbose_name_plural}
        for key, model in models_map.items()
    ]
    
    # Get the class paths from the model
    form_class_path   = selected_model.get_form_class()
    filter_class_path = selected_model.get_filter_class()
    table_class_path  = selected_model.get_table_class()
    
    # Import the actual classes using the helper function
    FormClass   = get_class_from_string(form_class_path)
    FilterClass = get_class_from_string(filter_class_path)
    TableClass  = get_class_from_string(table_class_path)
    
    # Instantiate the objects.
    # Check if an 'id' is provided in GET parameters to edit an instance
    instance_id = request.GET.get('id')
    if instance_id:
        try:
            instance = selected_model.objects.get(pk=instance_id)
            form = FormClass(request.POST or None, instance=instance)
        except selected_model.DoesNotExist:
            form = FormClass(request.POST or None)  # Fall back to a blank form if no instance is found
    else:
        form = FormClass(request.POST or None)

    # Set default ordering if no 'sort' parameter is provided
    sort_param = request.GET.get('sort', None)
    # If the 'sort' parameter doesn't exist, order by 'id' by default
    if not sort_param:
        # Default to ordering by 'id' if 'sort' parameter is not provided
        filter_obj = FilterClass(request.GET or None, queryset=selected_model.objects.all().order_by('id'))
    else:
        # For the filter, pass in the GET data and a queryset for the model.
        filter_obj = FilterClass(request.GET or None, queryset=selected_model.objects.all())
    
    # Instantiate the table from the filtered queryset.
    table = TableClass(filter_obj.qs, model_name=model_param, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action="UPDATE",
                model_name='ادارة الاقسام',
                object_id=instance.pk,
                number=selected_model._meta.verbose_name,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            print("Form is valid and saved.")
            return redirect('manage_sections')  # Change this to your desired redirect
        else:
            print("Form is not valid. Errors:", form.errors)

    RequestConfig(request, paginate={'per_page': 20}).configure(table)
    
    context = {
        'active_model': model_param,         # e.g., 'Country'
        'models': models_list,     # All four model names for the tabs
        'form': form,
        'filter': filter_obj,
        'table': table,
        'id': instance_id,  # Pass 'id' to the template context
        'ar_name': selected_model._meta.verbose_name,  # Add verbose_name to the context
        'ar_names': selected_model._meta.verbose_name_plural  # Add verbose_name to the context
    }
    
    return render(request, 'manage_sections.html', context)


# Views for Decree Model
#####################################################################
# Main table Function for Decree Model

def decree_list(request):
    # if not request.user.has_perm('documents.view_decree'):
    #     messages.error(request, "ليس لديك الصلاحية الكافية لزيارة هذا القسم!.")
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # Get the base queryset (only non-deleted items)
    if request.user.has_perm('documents.view_decree'):
        qs = Decree.objects.filter(deleted_at__isnull=True)
    else:
        qs = Decree.objects.filter(deleted_at__isnull=True, is_placeholder=False)
    # Get the status from GET parameters (None means "ALL")
    status = request.GET.get("status")
    if status is not None:
        try:
            status = int(status)
            if status in [choice[0] for choice in DecreeStatus.choices]:
                qs = qs.filter(status=status)
            else:
                status = None
        except ValueError:
            status = None

    # Dynamically import the filter class
    filter_class_path = Decree.get_filter_class()
    filter_class = get_class_from_string(filter_class_path)
    decree_filter = filter_class(request.GET, queryset=qs)

    # Dynamically import the table class
    table_class_path = Decree.get_table_class()
    table_class = get_class_from_string(table_class_path)
    table = table_class(decree_filter.qs)
    
    # Configure pagination (10 decrees per page)
    RequestConfig(request, paginate={'per_page': 20}).configure(table)
    
    return render(request, 'decrees/decree_list.html', {
        'table': table,
        'filter': decree_filter,
        'current_status': status,
        'status_choices': DecreeStatus.choices,

    })


# Adding and Editing Functions for Decree Model
# @login_required
# def add_edit_decree(request, document_id=None):
#     if not request.user.has_perm('documents.add_decree'):
#         messages.error(request, "ليس لديك الصلاحية الكافية للادخال والتعديل!.")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
#     if document_id:
#         instance = get_object_or_404(Decree, id=document_id)
#     else:
#         instance = None

#     # Dynamically import the form class
#     form_class_path = Decree.get_form_class()
#     form_class = get_class_from_string(form_class_path)
#     form = form_class(request.POST or None, request.FILES or None, instance=instance)
    
#     if request.method == 'POST' and form.is_valid():
#         # Add the check here for is_placeholder field
#         if instance and instance.is_placeholder:
#             instance.is_placeholder = False
#             instance.save()
#         instance = form.save()

#         # Log the action
#         UserActivityLog.objects.create(
#             user=request.user,
#             action="CREATE" if not document_id else "UPDATE",
#             model_name='قرار',
#             object_id=instance.pk,
#             number=instance.number,
#             timestamp=timezone.now(),
#             ip_address=get_client_ip(request),  # Assuming you have this function
#             user_agent=request.META.get("HTTP_USER_AGENT", ""),
#         )
#         return redirect(reverse('decree_list'))

#     return render(request, 'decrees/decree_form.html', {
#         'form': form,
#     })

@login_required
def add_decree(request):
    """Function to add a new Decree."""
    if not request.user.has_perm('documents.add_decree'):
        messages.error(request, "ليس لديك الصلاحية الكافية للإدخال!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    form_class_path = Decree.get_form_class()
    form_class = get_class_from_string(form_class_path)
    form = form_class(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        instance = form.save()

        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="CREATE",
            model_name='قرار',
            object_id=instance.pk,
            number=instance.number,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect(reverse('decree_list'))

    return render(request, 'decrees/decree_form.html', {'form': form})


@login_required
def edit_decree(request, document_id):
    """Function to edit an existing Decree."""
    if not request.user.has_perm('documents.change_decree'):
        messages.error(request, "ليس لديك الصلاحية الكافية للتعديل!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    instance = get_object_or_404(Decree, id=document_id)

    form_class_path = Decree.get_form_class()
    form_class = get_class_from_string(form_class_path)
    form = form_class(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        # Check if the decree was auto-created and remove placeholder flag
        if instance.is_placeholder:
            instance.is_placeholder = False
            instance.save()

        instance = form.save()

        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="UPDATE",
            model_name='قرار',
            object_id=instance.pk,
            number=instance.number,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect(reverse('decree_list'))

    return render(request, 'decrees/decree_form.html', {'form': form})


# PDF download Function for Decree Model
def download_decree(request, document_id):
    """
    Downloads a decree's PDF file, attachment, or both as a ZIP file.
    """
    # if not request.user.has_perm('documents.download_decree'):
    #     messages.error(request, "ليس لديك الصلاحية الكافية لتحميل هذا الملف!.")
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    decree = get_object_or_404(Decree, pk=document_id)

    # Determine file existence
    pdf_exists = decree.pdf_file and decree.pdf_file.name
    attach_exists = decree.attach and decree.attach.name

    if not pdf_exists and not attach_exists:
        return JsonResponse({'error': 'No document or attachment available for download.'}, status=404)

    # Prepare file naming
    date_str = decree.date.strftime('%Y-%m-%d') if decree.date else 'unknown_date'
    identifier = decree.number if decree.number else 'unknown'

    if pdf_exists and attach_exists:
        # Create ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Add PDF to ZIP
            pdf_filename = f"decree_{identifier}_{date_str}.pdf"
            with decree.pdf_file.open('rb') as pdf_file:
                zip_file.writestr(pdf_filename, pdf_file.read())

            # Add attachment to ZIP
            attach_ext = decree.attach.name.split('.')[-1]
            attach_filename = f"decree_attachment_{identifier}_{date_str}.{attach_ext}"
            with decree.attach.open('rb') as attach_file:
                zip_file.writestr(attach_filename, attach_file.read())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="decree_{identifier}_{date_str}.zip"'
        return response

    elif pdf_exists:
        # Download only PDF
        content_type, _ = mimetypes.guess_type(decree.pdf_file.name) or ('application/pdf',)
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="decree_{identifier}_{date_str}.pdf"'

        with decree.pdf_file.open('rb') as pdf_file:
            response.write(pdf_file.read())

        return response

    elif attach_exists:
        # Download only attachment
        content_type, _ = mimetypes.guess_type(decree.attach.name) or ('application/octet-stream',)
        attach_ext = decree.attach.name.split('.')[-1]
        attach_filename = f"decree_attachment_{identifier}_{date_str}.{attach_ext}"
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{attach_filename}"'

        with decree.attach.open('rb') as attach_file:
            response.write(attach_file.read())

        return response

    return HttpResponseNotFound('No document or attachment available for download.')


# Soft delete Function for Decree Model
@login_required
@user_passes_test(is_superuser)
def soft_delete_decree(request, document_id):
    """
    Soft-delete a decree by setting its deleted_at timestamp.
    """
    if request.method == 'POST':  # Change from DELETE to POST
        document = get_object_or_404(Decree, id=document_id)
        document.deleted_at = timezone.now()  # Set the deletion timestamp
        document.save()
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="DELETE",
            model_name='قرار',
            object_id=document.pk,
            number=document.number,  # Save the relevant number
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Detail Function for Decree Model
def decree_detail(request, document_id):
    """
    Displays details of a decree with a PDF preview.
    """
    # if not request.user.has_perm('documents.view_decree'):
    #     messages.error(request, "ليس لديك الصلاحية الكافية لزيارة هذا القسم!.")
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    decree = get_object_or_404(Decree, pk=document_id)
    # Log the action
    UserActivityLog.objects.create(
        user=user,
        action="VIEW",
        model_name='قرار',
        object_id=decree.pk,
        number=decree.number,  # Save the relevant number
        timestamp=timezone.now(),
        ip_address=get_client_ip(request),  # Assuming you have this function
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    return render(request, 'decrees/decree_detail.html', {'decree': decree})


# Views for Publication Model
#####################################################################
# Main table Function for Publication Model
def publication_list(request):
    
    qs = Publication.objects.filter(deleted_at__isnull=True)

    # Get the status from GET parameters (None means "ALL")
    status = request.GET.get("status")
    if status is not None:
        try:
            status = int(status)
            if status in [choice[0] for choice in PublicationStatus.choices]:
                qs = qs.filter(status=status)
            else:
                status = None
        except ValueError:
            status = None

    # Dynamically import the filter class
    filter_class_path = Publication.get_filter_class()
    filter_class = get_class_from_string(filter_class_path)
    publication_filter = filter_class(request.GET, queryset=qs)

    # Dynamically import the table class
    table_class_path = Publication.get_table_class()
    table_class = get_class_from_string(table_class_path)
    table = table_class(publication_filter.qs)

    RequestConfig(request, paginate={'per_page': 20}).configure(table)

    return render(request, "publications/pub_list.html", {
        "table": table,
        "filter": publication_filter,
        "current_status": status,
        "status_choices": PublicationStatus.choices,

    })


# Adding Function for Publication Model
@login_required
def add_publication(request):
    form_class_path = Publication.get_form_class()
    form_class = get_class_from_string(form_class_path)
    form = form_class(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        publication = form.save()

        decree_number = form.cleaned_data['decree_number']
        selected_year = form.cleaned_data['year']
        decree_owner = form.cleaned_data['owner']
        decree_country = form.cleaned_data['country']
        decree_category = form.cleaned_data['category']
        decree_date_applied = form.cleaned_data['date_applied']
        decree_number_applied = form.cleaned_data['number_applied']
        decree_ar_brand = form.cleaned_data['ar_brand']
        decree_en_brand = form.cleaned_data['en_brand']

        decree = Decree.objects.filter(number=decree_number, date__year=selected_year).first()
        
        if not decree:
            decree = Decree.objects.create(
                number=decree_number,
                date=datetime.date(int(selected_year), 1, 1),
                company=decree_owner,
                country=decree_country,
                category=decree_category,
                date_applied=decree_date_applied,
                number_applied=decree_number_applied,
                ar_brand=decree_ar_brand,
                en_brand=decree_en_brand,
                is_placeholder=True,
            )
            UserActivityLog.objects.create(
                user=request.user,
                action="CREATE",
                model_name='قرار مؤقت',
                object_id=decree.pk,
                number=decree.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

        publication.decree = decree
        publication.save()
        
        UserActivityLog.objects.create(
            user=request.user,
            action="CREATE",
            model_name='اشهار',
            object_id=publication.pk,
            number=publication.number,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect(reverse('publication_list'))

    return render(request, 'publications/pub_form.html', {'form': form})


# Editing Function for Publication Model
@login_required
def edit_publication(request, document_id):
    instance = get_object_or_404(Publication, id=document_id)
    
    form_class_path = Publication.get_form_class()
    form_class = get_class_from_string(form_class_path)
    form = form_class(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        publication = form.save()

        UserActivityLog.objects.create(
            user=request.user,
            action="UPDATE",
            model_name='اشهار',
            object_id=publication.pk,
            number=publication.number,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect(reverse('publication_list'))

    return render(request, 'publications/pub_form_edit.html', {'form': form})


# PDF download Function for Publication Model
def download_publication(request, document_id):
    """
    Downloads a publication's image file or attachment as a ZIP file.
    """
    publication = get_object_or_404(Publication, pk=document_id)

    # Check for image and attachment existence
    img_exists = publication.img_file and publication.img_file.name
    attach_exists = publication.attach and publication.attach.name

    if not img_exists and not attach_exists:
        return JsonResponse({'error': 'No document or attachment available for download.'}, status=404)

    # Prepare file naming
    date_str = publication.created_at.strftime('%Y-%m-%d') if publication.created_at else 'unknown_date'
    identifier = publication.number if publication.number else 'unknown'

    if img_exists and attach_exists:
        # Create ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Add Image to ZIP
            img_filename = f"publication_{identifier}_{date_str}.jpg"
            with publication.img_file.open('rb') as img_file:
                zip_file.writestr(img_filename, img_file.read())

            # Add attachment to ZIP
            attach_ext = publication.attach.name.split('.')[-1]
            attach_filename = f"publication_attachment_{identifier}_{date_str}.{attach_ext}"
            with publication.attach.open('rb') as attach_file:
                zip_file.writestr(attach_filename, attach_file.read())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="publication_{identifier}_{date_str}.zip"'
        return response

    elif img_exists:
        # Download only image
        content_type, _ = mimetypes.guess_type(publication.img_file.name) or ('image/jpeg',)
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="publication_{identifier}_{date_str}.jpg"'

        with publication.img_file.open('rb') as img_file:
            response.write(img_file.read())

        return response

    elif attach_exists:
        # Download only attachment
        content_type, _ = mimetypes.guess_type(publication.attach.name) or ('application/octet-stream',)
        attach_ext = publication.attach.name.split('.')[-1]
        attach_filename = f"publication_attachment_{identifier}_{date_str}.{attach_ext}"
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{attach_filename}"'

        with publication.attach.open('rb') as attach_file:
            response.write(attach_file.read())

        return response

    return HttpResponseNotFound('No document or attachment available for download.')


# Soft delete Function for Publication Model
@login_required
@user_passes_test(is_superuser)
def soft_delete_publication(request, document_id):
    """
    Soft-delete a publication by setting its deleted_at timestamp.
    """
    if request.method == 'POST':  # Change from DELETE to POST
        document = get_object_or_404(Publication, id=document_id)
        document.deleted_at = timezone.now()  # Set the deletion timestamp
        document.save()
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="DELETE",
            model_name='اشهار',
            object_id=document.pk,
            number=document.number,  # Save the relevant number
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Detail Function for Publication Model
def publication_detail(request, document_id):
    """
    Displays details of a publication with image preview.
    """
    publication = get_object_or_404(Publication, pk=document_id)
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    # Fetch the decree if it exists
    decree = publication.decree
    # Log the action
    UserActivityLog.objects.create(
        user=user,
        action="VIEW",
        model_name='اشهار',
        object_id=publication.pk,
        number=publication.number,  # Save the relevant number
        timestamp=timezone.now(),
        ip_address=get_client_ip(request),  # Assuming you have this function
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    return render(request, 'publications/pub_detail.html', {
        'publication': publication,
        'decree': decree  # Pass the decree object
    })


# Function for changing status of an intial publication to final using a button
@login_required
@permission_required('documents.can_change_status', raise_exception=True)  # Check for specific permission
def update_status(request, document_id):
    """
    Update publication status from 'initial' (1) to 'final' (3).
    """
    if request.method == 'POST':  # Handling POST request for status change
        publication = get_object_or_404(Publication, id=document_id)
        # Check if the publication is in 'initial' status
        if publication.status == 1:

            publication.status = 3
            publication.decree.is_published = True
            publication.decree.save()
            publication.save()
            messages.success(request, f"تم تغيير حالة الاشهار رقم {publication.number} إلى 'نشر نهائي'.")
        else:
            messages.error(request, "لا يمكن تغيير حالة هذه الوثيقة لأنها ليست في الحالة 'مبدئي'.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Function for fetching publication data for PDF generation:
def fetch_pub_data(pub_id):
    # Fetch the import record based on trans_id
    pub_record = get_object_or_404(Publication, id=pub_id)
    # Prepare the record details
    pub_record = {
        'pub_id': pub_record.id,
        'pub_year': pub_record.year,
        'pub_date': pub_record.created_at.strftime("%Y-%m-%d"),
        'pub_no': pub_record.number,
        'dec_no': pub_record.decree.number if pub_record.decree else "N/A",
        'applicant': pub_record.applicant if pub_record.applicant else "N/A",
        'owner': pub_record.owner if pub_record.owner else "N/A",
        'country': pub_record.country.ar_name if pub_record.country else "N/A",
        'address': pub_record.address if pub_record.address else "N/A",
        'date_applied': pub_record.date_applied.strftime("%Y-%m-%d") if pub_record.date_applied else "N/A",
        'number_applied': pub_record.number_applied if pub_record.number_applied else "N/A",
        'ar_brand': pub_record.ar_brand if pub_record.ar_brand else "N/A",
        'en_brand': pub_record.en_brand if pub_record.en_brand else "N/A",
        'category': pub_record.category if pub_record.category else "N/A",
        'pub_img': pub_record.img_file.url if pub_record.img_file else "N/A",
        'e_number': pub_record.e_number if pub_record.e_number else "N/A",
        'status': pub_record.status if pub_record.status else "N/A",
        'notes': pub_record.notes or "N/A",
    }

    print(f'fetched record info for Import Record No {pub_id} successfully')
    return pub_record


# Function for generating INITIAL PDF for Publication Model
def gen_pub_pdf(request, pub_id):
    record_info = fetch_pub_data(pub_id)
    pub_qr = generate_pub_qr(pub_id)
    pdf_data = pub_pdf(pub_id, record_info, pub_qr)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pub_id}.pdf"'

    return response


# Function for generating FINAL PDF for Publication Model
def gen_final_pub_pdf(request, pub_id):
    # if model == 'publication':
    record_info = fetch_pub_data(pub_id)
    pdf_data = pub_final_pdf(pub_id, record_info)
    # else:
    #     return HttpResponse("Invalid model type", status=400)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pub_id}.pdf"'

    return response


# Views for Objection Model
#####################################################################
# Main table Function for Objection Model
@login_required
def objection_list(request):
    
    # Check if the user has the required permission
    if not request.user.has_perm('documents.view_objection'):
        messages.error(request, "ليس لديك الصلاحية الكافية لزيارة هذا القسم!.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # Get the base queryset (only non-deleted items)
    qs = Objection.objects.filter(deleted_at__isnull=True)

    # Get the status from GET parameters (None means "ALL")
    status = request.GET.get("status")
    if status is not None:
        try:
            status = int(status)
            if status in [choice[0] for choice in ObjectionStatus.choices]:
                qs = qs.filter(status=status)
            else:
                status = None
        except ValueError:
            status = None

    # Get the filter class and apply it
    filter_class_path = Objection.get_filter_class()
    filter_class = get_class_from_string(filter_class_path)
    objection_filter = filter_class(request.GET, queryset=qs)
    
    # Get the table class and create the table based on the filtered queryset
    table_class_path = Objection.get_table_class()
    table_class = get_class_from_string(table_class_path)
    table = table_class(objection_filter.qs)
    
    # Configure pagination (10 objections per page)
    RequestConfig(request, paginate={'per_page': 20}).configure(table)
    
    return render(request, 'objections/objection_list.html', {
        'table': table,
        'filter': objection_filter,
        'current_status': status,
        'status_choices': ObjectionStatus.choices,
    })


# Adding Function for Objection Model
def add_objection(request):
    form_class = get_class_from_string(Objection.get_form_class())  # Resolving the form class

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            pub_id = form.cleaned_data.get("pub_id")  # Get the pub_id
            publication = get_object_or_404(Publication, id=pub_id, deleted_at__isnull=True)
            
            print(f"Found Publication: {publication}")  # Debugging output

            objection = form.save(commit=False)
            objection.pub = publication  # Assign the publication object, not just the ID
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="CREATE",
                model_name='اعتراض من مستخدم',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, "Objection added successfully!")
            return redirect("objection_list")

        else:
            print(form.errors)  # Debugging: Print form errors if invalid

    else:
        form = form_class(request.POST or None, request.FILES or None)

    return render(request, 'objections/objection_form.html', {'form': form})


# Editing Function for Objection Model
def edit_objection(request, document_id):
    """
    Function to edit an existing objection.
    """
    form_class = get_class_from_string(Objection.get_form_class(context="objection_pub_pick"))  # Resolving the form class
    objection = get_object_or_404(Objection, id=document_id)  # Get the existing Objection object
    publication = objection.pub  # Get the associated Publication for the existing Objection

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=objection)
        if form.is_valid():
            objection = form.save(commit=False)
            objection.pub = publication  # Assign the publication object, not just the ID
            if objection.status == 1:
                if form.cleaned_data.get('is_paid') and form.cleaned_data.get('receipt_file'):
                    objection.status = 2
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="UPDATE",
                model_name='اعتراض من عضو',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, "Objection updated successfully!")
            return redirect("objection_list")
        else:
            print(form.errors)  # Debugging: Print form errors if invalid

    else:
        form = form_class(instance=objection)

    return render(request, 'objections/objection_form_edit.html', {'form': form, 'objection': objection, 'publication': publication})


# Public Publication Selection for Objection Function
def objection_pub_pick(request):
    qs = Publication.objects.filter(deleted_at__isnull=True, status=1)

    # Use the same filter logic but for status=1 only
    filter_class = get_class_from_string(Publication.get_filter_class(context="objection_pub_pick"))
    publication_filter = filter_class(request.GET, queryset=qs)

    # Use a separate table for the new page
    table_class = get_class_from_string(Publication.get_table_class(context="objection_pub_pick"))
    table = table_class(publication_filter.qs)

    RequestConfig(request, paginate={'per_page': 20}).configure(table)

    return render(request, "objections/objection_pub_pick.html", {
        "table": table,
        "filter": publication_filter,
    })


# Public Function for Adding an Objection
def add_pub_objection(request, document_id=None):
    """
    Function to add a new objection for a given publication for the public.
    """
    form_class = get_class_from_string(Objection.get_form_class(context="objection_pub_pick"))  # Resolving the form class
    
    if document_id:
        publication = get_object_or_404(Publication, id=document_id, deleted_at__isnull=True)  # Get the publication
        
    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            objection = form.save(commit=False)
            objection.pub = publication
            
            # Check the values of is_paid and receipt_file directly in the if statement
            if form.cleaned_data.get('is_paid') and form.cleaned_data.get('receipt_file'):
                objection.status = 2
            else:
                objection.status = 1
            objection.save()
            
            # Log the objection creation
            UserActivityLog.objects.create(
                user=None,
                action="CREATE",
                model_name='اعتراض من شخص',
                object_id=objection.pk,
                ip_address = get_client_ip(request),
                user_agent = request.META.get("HTTP_USER_AGENT", ""),
                number=objection.number,
                timestamp=timezone.now(),
            )
            
            qr_buffer = generate_obj_qr(objection.unique_code)
            qr_base64 = buffer_to_base64(qr_buffer)
            # Prepare the success message with the PDF link
            success_msg = f"""
                <div style="display: flex; align-items: center;">
                    <div style="flex: 1; margin-right: 10px;">
                        <p>رقم تتبع الاعتراض هو: <strong>{objection.unique_code}</strong></p>
                        <p>احفظه لكي تتمكن لاحقا من مراجعة حالة اعتراضك.</p>
                        <p>يرجى تحميل نموذج الاعتراض <a href='{reverse('gen_obj_pdf', kwargs={'obj_id': objection.id})}' target='_blank'>من هنا</a>.</p>
                        <p>و استكمال نواقصه و توقيعه و تقديمه الى مكتب العلامات التجارية.</p>
                    </div>
                    <img src='data:image/png;base64,{qr_base64}' alt='QR Code' style='width: 250px; height: auto;' />  <!-- Adjust the width as needed -->
                </div>
            """

            # Mark the message as safe to render HTML
            messages.success(request, mark_safe(success_msg))

            return redirect('index')  # Redirect to the index page
        else:
            print(form.errors)  # Debugging: Print form errors if invalid

    else:
        form = form_class()
    
    return render(request, 'objections/objection_pub_form.html', {'form': form, 'publication': publication})


# Function for fetching objection data for PDF generation
def fetch_objection_data(obj_id):
    # Fetch the objection record based on its ID
    obj_record = get_object_or_404(Objection, id=obj_id)
    
    # Prepare the record details
    objection_data = {
        'obj_id': obj_record.id,
        'obj_number': obj_record.number,
        'pub_id': obj_record.pub.id if obj_record.pub else "N/A",
        'pub_no': obj_record.pub.number if obj_record.pub else "N/A",
        'pub_year': obj_record.pub.year if obj_record.pub else "N/A",
        'pub_date': obj_record.pub.created_at.strftime("%Y-%m-%d") if obj_record.pub else "N/A",
        'applicant': obj_record.pub.applicant if obj_record.pub and obj_record.pub.applicant else "N/A",
        'number_applied': obj_record.pub.number_applied if obj_record.pub and obj_record.pub.number_applied else "N/A",
        'e_number': obj_record.pub.e_number if obj_record.pub and obj_record.pub.e_number else "N/A",
        'owner': obj_record.pub.owner if obj_record.pub and obj_record.pub.owner else "N/A",
        'obj_date': obj_record.created_at.strftime("%Y-%m-%d"),
        'name': obj_record.name,
        'job': obj_record.job,
        'nationality': obj_record.nationality.ar_name if obj_record.nationality else "N/A",
        'address': obj_record.address,
        'phone': obj_record.phone,
        'com_name': obj_record.com_name,
        'com_job': obj_record.com_job.name if obj_record.com_job else "N/A",
        'com_address': obj_record.com_address,
        'com_og_address': obj_record.com_og_address,
        'com_mail_address': obj_record.com_mail_address,
        'status': obj_record.get_status_display(),
        'reason': obj_record.reason if obj_record.reason else "N/A",
        'is_paid': "Yes" if obj_record.is_paid else "No",
        'receipt_file': obj_record.receipt_file.url if obj_record.receipt_file else "N/A",
        'unique_code': obj_record.unique_code,
        'notes': obj_record.notes or "N/A",
    }

    print(f'Fetched record info for Objection No {obj_id} successfully')
    return objection_data


# Function for generating PDF for Objection Model
def gen_obj_pdf(request, obj_id):
    """
    Generates and returns a PDF for the specified objection.
    """
    # Fetch objection data
    obj_record = fetch_objection_data(obj_id)
    obj_qr = generate_obj_qr(obj_record['unique_code'])
    # Generate the PDF (assuming a `obj_pdf` function exists similar to `pub_pdf`)
    pdf_data = obj_pdf(obj_id, obj_record, obj_qr)

    # Return the PDF as a response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="objection_{obj_id}.pdf"'

    return response


# PDF download Function for Objection Attachment
@login_required
def download_objection(request, document_id):
    """
    Downloads an objection's PDF file.
    """
    objection = get_object_or_404(Objection, pk=document_id)

    # Check if PDF exists
    pdf_exists = objection.pdf_file and objection.pdf_file.name

    if not pdf_exists:
        return JsonResponse({'error': 'No PDF document available for download.'}, status=404)

    # Prepare file naming
    date_str = objection.created_at.strftime('%Y-%m-%d') if objection.created_at else 'unknown_date'
    identifier = objection.number if objection.number else 'unknown'

    # Download only PDF
    content_type, _ = mimetypes.guess_type(objection.pdf_file.name) or ('application/pdf',)
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="objection_{identifier}_{date_str}.pdf"'

    with objection.pdf_file.open('rb') as pdf_file:
        response.write(pdf_file.read())

    return response


# PDF download Function for Objection Receipt
@login_required
def download_objection_receipt(request, document_id):
    """
    Downloads an objection's PDF receipt.
    """
    objection = get_object_or_404(Objection, pk=document_id)

    # Check if PDF exists
    pdf_exists = objection.receipt_file and objection.receipt_file.name

    if not pdf_exists:
        return JsonResponse({'error': 'No PDF document available for download.'}, status=404)

    # Prepare file naming
    date_str = objection.created_at.strftime('%Y-%m-%d') if objection.created_at else 'unknown_date'
    identifier = objection.number if objection.number else 'unknown'

    # Download only PDF
    content_type, _ = mimetypes.guess_type(objection.receipt_file.name) or ('application/pdf',)
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="objection_{identifier}_{date_str}.pdf"'

    with objection.receipt_file.open('rb') as pdf_file:
        response.write(pdf_file.read())

    return response


# Soft delete Function for Objection Model
@login_required
@user_passes_test(is_superuser)
def soft_delete_objection(request, document_id):
    """
    Soft-delete an objection by setting its deleted_at timestamp.
    """
    if request.method == 'POST':  # Change from DELETE to POST
        document = get_object_or_404(Objection, id=document_id)
        document.deleted_at = timezone.now()  # Set the deletion timestamp
        document.save()
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="DELETE",
            model_name='معارضة',
            object_id=document.pk,
            number=document.number,  # Save the relevant number
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Detail Function for Objection Model
@login_required
def objection_detail(request, document_id):
    """
    Displays details of an objection with a PDF preview.
    """
    objection = get_object_or_404(Objection, pk=document_id)
    # Log the action
    UserActivityLog.objects.create(
        user=request.user,
        action="VIEW",
        model_name='اعتراض',
        object_id=objection.pk,
        number=objection.number,
        timestamp=timezone.now(),
        ip_address=get_client_ip(request),  # Assuming you have this function
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    return render(request, 'objections/objection_detail.html', {'objection': objection})


# Public Function for checking an objection status
@csrf_exempt  # Allow AJAX requests without CSRF token (only if necessary)
def check_objection_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            unique_code = data.get("unique_code")
            phone_number = data.get("phone_number")

            # Query the database for the objection
            objection = Objection.objects.filter(unique_code=unique_code, phone=phone_number).first()

            if objection:
                return JsonResponse({
                    "success": True,
                    "status": objection.get_status_display(),
                    "com_name": objection.com_name,
                    "brand": f"{objection.pub.ar_brand} - {objection.pub.en_brand} <br> الفئة: {objection.pub.category}",
                    "date": objection.created_at.strftime("%d-%m-%Y"),
                    "file": reverse('gen_obj_pdf', kwargs={'obj_id': objection.id})
                })
            else:
                return JsonResponse({"success": False, "error": "لم يتم العثور على اعتراض مطابق."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "طلب غير صالح."}, status=400)


# Function for changing status of an Unconfirmed objection to Paid using a button
@login_required
@permission_required('documents.confirm_objection_fee', raise_exception=True)
def confirm_objection_fee(request, document_id):
    """
    Update Objection status from (unconfirm) to (paid).
    """
    if request.method == 'POST':
        objection = get_object_or_404(Objection, id=document_id)
        # Check if the objection is in 'unconfirm' status
        if objection.status <= 2:

            objection.status = 3
            objection.is_paid = True
            objection.pub.status = 2
            objection.pub.save()
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="CONFIRM",
                model_name='رسوم اعتراض',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, f"تم تغيير حالة المعارضة رقم {objection.number} إلى 'تم الدفع'.")
        else:
            messages.error(request, "لا يمكن تغيير حالة هذه المعارضة ، حدث خطأ ما!'.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Function for changing status of an Unconfirmed objection to Rejected using a button
@login_required
@permission_required('documents.confirm_objection_fee', raise_exception=True)
def decline_objection_fee(request, document_id):
    """
    Update Objection status from (unconfirm) to (reject).
    """
    if request.method == 'POST':
        objection = get_object_or_404(Objection, id=document_id)
        # Check if the objection is in 'unconfirm' status
        if objection.status <= 2:

            objection.status = 5
            objection.is_paid = False
            other_objections = Objection.objects.filter(pub=objection.pub).exclude(id=objection.id)
            if not other_objections.exists():
                objection.pub.status = 1  # Set the publication status to 1 if no other objections exist

            objection.pub.save()
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="REJECT",
                model_name='رسوم اعتراض',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, f"تم تغيير حالة المعارضة رقم {objection.number} إلى 'رفض'.")
        else:
            messages.error(request, "لا يمكن تغيير حالة هذه المعارضة ، حدث خطأ ما!'.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Function for changing status of an Paid objection to Accept using a button
@login_required
@permission_required('documents.confirm_objection_status', raise_exception=True)
def confirm_objection_status(request, document_id):
    """
    Update Objection status from (paid) to (accept).
    """
    if request.method == 'POST':
        objection = get_object_or_404(Objection, id=document_id)
        # Check if the objection is in 'unconfirm' status
        if objection.status == 3:

            objection.status = 4
            objection.pub.status = 4
            objection.pub.save()
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="CONFIRM",
                model_name='اعتراض',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, f"تم تغيير حالة المعارضة رقم {objection.number} إلى 'قبول'.")
        else:
            messages.error(request, "لا يمكن تغيير حالة هذه المعارضة ، حدث خطأ ما!'.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Function for changing status of an Unconfirmed objection to Rejected using a button
@login_required
@permission_required('documents.confirm_objection_status', raise_exception=True)
def decline_objection_status(request, document_id):
    """
    Update Objection status from (paid) to (reject).
    """
    if request.method == 'POST':
        objection = get_object_or_404(Objection, id=document_id)
        # Check if the objection is in 'unconfirm' status
        if objection.status == 3:

            objection.status = 5
            other_objections = Objection.objects.filter(pub=objection.pub).exclude(id=objection.id)
            if not other_objections.exists():
                objection.pub.status = 1  # Set the publication status to 1 if no other objections exist

            objection.pub.save()
            objection.save()
            # Log the action
            UserActivityLog.objects.create(
                user=request.user,
                action="REJECT",
                model_name='اعتراض',
                object_id=objection.pk,
                number=objection.number,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request),  # Assuming you have this function
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            messages.success(request, f"تم تغيير حالة المعارضة رقم {objection.number} إلى 'رفض'.")
        else:
            messages.error(request, "لا يمكن تغيير حالة هذه المعارضة ، حدث خطأ ما!'.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Views for FormPlus Model
#####################################################################
# Main table Function for FormPlus Model
def formplus_list(request):
    # Get the base queryset (only non-deleted items)
    qs = FormPlus.objects.filter(deleted_at__isnull=True)
    
    # Dynamically import the filter class
    filter_class_path = FormPlus.get_filter_class()
    filter_class = get_class_from_string(filter_class_path)
    formplus_filter = filter_class(request.GET, queryset=qs)

    # Dynamically import the table class
    table_class_path = FormPlus.get_table_class()
    table_class = get_class_from_string(table_class_path)
    table = table_class(formplus_filter.qs)
    
    # Configure pagination (10 decrees per page)
    RequestConfig(request, paginate={'per_page': 20}).configure(table)
    
    return render(request, 'formplus/formplus_list.html', {
        'table': table,
        'filter': formplus_filter,
    })


# Adding and Editing view for FormPlus Model
@login_required
def add_edit_formplus(request, document_id=None):
    if not request.user.has_perm('documents.add_formplus'):
        messages.error(request, "ليس لديك الصلاحية الكافية للادخال والتعديل!.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    instance = get_object_or_404(FormPlus, id=document_id) if document_id else None

    # Dynamically import the form class
    form_class_path = FormPlus.get_form_class()
    form_class = get_class_from_string(form_class_path)
    form = form_class(request.POST or None, request.FILES or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        instance = form.save()
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="CREATE" if not document_id else "UPDATE",
            model_name='تشريع او نموذج',
            object_id=instance.pk,
            number=instance.number,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect(reverse('formplus_list'))  # Adjust URL name as needed

    return render(request, 'formplus/formplus_form.html', {'form': form})


# PDF download Function for FormPlus Model
def download_formplus_pdf(request, document_id):
    """
    Downloads a FormPlus document's PDF file.
    """
    formplus = get_object_or_404(FormPlus, pk=document_id)

    # Check if the PDF file exists
    if not formplus.pdf_file or not formplus.pdf_file.name:
        return JsonResponse({'error': 'No document available for download.'}, status=404)

    # Prepare file naming
    date_str = formplus.date.strftime('%Y-%m-%d') if formplus.date else 'unknown_date'
    identifier = formplus.number if formplus.number else 'unknown'
    pdf_filename = f"formplus_{identifier}_{date_str}.pdf"

    # Set content type and response
    content_type, _ = mimetypes.guess_type(formplus.pdf_file.name) or ('application/pdf',)
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

    # Serve the PDF file
    with formplus.pdf_file.open('rb') as pdf_file:
        response.write(pdf_file.read())

    return response


# PDF download Function for FormPlus Model
def download_formplus_word(request, document_id):
    """
    Downloads a FormPlus document's Word file.
    """
    formplus = get_object_or_404(FormPlus, pk=document_id)

    # Check if the Word file exists
    if not formplus.word_file or not formplus.word_file.name:
        return JsonResponse({'error': 'No document available for download.'}, status=404)

    # Prepare file naming
    date_str = formplus.date.strftime('%Y-%m-%d') if formplus.date else 'unknown_date'
    identifier = formplus.number if formplus.number else 'unknown'
    word_filename = f"formplus_{identifier}_{date_str}.docx"

    # Set content type for Word files
    content_type, _ = mimetypes.guess_type(formplus.word_file.name)
    content_type = content_type or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{word_filename}"'

    # Serve the Word file
    with formplus.word_file.open('rb') as word_file:
        response.write(word_file.read())

    return response


# Soft delete Function for FormPlus Model
@login_required
@user_passes_test(is_superuser)
def soft_delete_formplus(request, document_id):
    """
    Soft-delete a FormPlus document by setting its deleted_at timestamp.
    """
    if request.method == 'POST':  # Change from DELETE to POST
        document = get_object_or_404(FormPlus, id=document_id)
        document.deleted_at = timezone.now()  # Set the deletion timestamp
        document.save()
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action="DELETE",
            model_name='تشريع او نموذج',
            object_id=document.pk,
            number=document.number,  # Save the relevant number
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# Detail Function for FormPlus Model
def formplus_detail(request, document_id):
    """
    Displays details of a FormPlus document with a PDF preview.
    """
    formplus = get_object_or_404(FormPlus, pk=document_id)
    
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    # Log the action
    UserActivityLog.objects.create(
        user=user,
        action="VIEW",
        model_name='تشريع او نموذج',
        object_id=formplus.pk,
        number=formplus.number,  # Save the relevant number
        timestamp=timezone.now(),
        ip_address=get_client_ip(request),  # Assuming you have this function
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    return render(request, 'formplus/formplus_detail.html', {'formplus': formplus})


# Views for Report Generation
#####################################################################
# Function that formts missing numbers in a table
def format_missing_numbers(missing_numbers):
    if not missing_numbers:
        return "<p>لا توجد أرقام مفقودة.</p>"

    formatted = []
    start = missing_numbers[0]
    end = start

    for num in missing_numbers[1:]:
        if num == end + 1:
            end = num
        else:
            if start == end:
                formatted.append(str(start))
            else:
                formatted.append(f"{start} الى {end}")
            start = end = num

    # Add the last range or number
    if start == end:
        formatted.append(str(start))
    else:
        formatted.append(f"{start} الى {end}")

    # Create an HTML table with a single row and multiple columns
    table_cells = ''.join(f'<td>{item}</td>' for item in formatted)
    return f'<table class="table"><tr>{table_cells}</tr></table>'


# Report by year for the model Decree
@login_required
def decree_report(request):
    years = Decree.objects.dates('date', 'year').distinct()
    selected_year = request.GET.get('year')

    # Initialize report data
    report_data = {}

    if selected_year:
        # Filter decrees for the selected year
        decrees = Decree.objects.filter(date__year=selected_year)

        # Calculate required metrics
        report_data['total_decrees'] = decrees.count()
        # Get the first and last decree details
        first_decree = decrees.order_by('number').first()  # Get the first decree based on number
        last_decree = decrees.order_by('-number').first()  # Get the last decree based on number
        
        if first_decree:
            report_data['first_decree_number'] = first_decree.number
            report_data['first_decree_date'] = first_decree.date

        if last_decree:
            report_data['last_decree_number'] = last_decree.number
            report_data['last_decree_date'] = last_decree.date

        # Calculate missing decrees
        first_decree_number = report_data.get('first_decree_number')
        last_decree_number = report_data.get('last_decree_number')
        
        report_data['missing_decrees'] = []
        if first_decree_number is not None and last_decree_number is not None:
            all_decree_numbers = set(decrees.values_list('number', flat=True))
            complete_range = set(range(first_decree_number, last_decree_number + 1))
            report_data['missing_decrees'] = list(complete_range - all_decree_numbers)

        report_data['total_missing'] = len(report_data['missing_decrees'])
        report_data['formatted_missing_decrees'] = format_missing_numbers(sorted(report_data['missing_decrees']))
        report_data['total_without_pdf'] = decrees.filter(Q(pdf_file__isnull=True) | Q(pdf_file='')).count()
        report_data['total_without_data'] = decrees.filter(
            Q(ar_brand__isnull=True) | Q(ar_brand='') | Q(en_brand__isnull=True) | Q(en_brand='')
        ).count()
        report_data['status_1_count'] = decrees.filter(status=1).count()
        report_data['status_2_count'] = decrees.filter(status=2).count()
        report_data['status_3_count'] = decrees.filter(status=3).count()
        report_data['status_4_count'] = decrees.filter(status=4).count()

    return render(request, 'decrees/decree_report.html', {
        'years': years,
        'selected_year': selected_year,
        'report_data': report_data,
    })


# Report by year for the model Publication
@login_required
def publication_report(request):
    years = Publication.objects.dates('date_applied', 'year').distinct()
    selected_year = request.GET.get('year')

    # Initialize report data
    report_data = {}

    if selected_year:
        # Filter publications for the selected year
        publications = Publication.objects.filter(date_applied__year=selected_year)

        # Calculate required metrics
        report_data['total_publications'] = publications.count()
        first_publication = publications.order_by('e_number').first()  # Get the first publication based on e_number
        last_publication = publications.order_by('-e_number').first()  # Get the last publication based on e_number
        
        if first_publication:
            report_data['first_publication_number'] = first_publication.e_number
            report_data['first_publication_date'] = first_publication.date_applied

        if last_publication:
            report_data['last_publication_number'] = last_publication.e_number
            report_data['last_publication_date'] = last_publication.date_applied

        # Calculate missing publications
        first_publication_number = report_data.get('first_publication_number')
        last_publication_number = report_data.get('last_publication_number')
        
        report_data['missing_publications'] = []
        if first_publication_number is not None and last_publication_number is not None:
            all_publication_numbers = set(publications.values_list('e_number', flat=True))
            complete_range = set(range(first_publication_number, last_publication_number + 1))
            report_data['missing_publications'] = list(complete_range - all_publication_numbers)

        report_data['total_missing'] = len(report_data['missing_publications'])
        report_data['formatted_missing_publications'] = format_missing_numbers(sorted(report_data['missing_publications']))
        report_data['total_without_img'] = publications.filter(Q(img_file__isnull=True) | Q(img_file='')).count()
        report_data['total_without_pdf'] = publications.filter(Q(attach__isnull=True) | Q(attach='')).count()
        report_data['total_without_data'] = publications.filter(
            Q(ar_brand__isnull=True) | Q(ar_brand='') | Q(en_brand__isnull=True) | Q(en_brand='')
        ).count()
        report_data['status_1_count'] = publications.filter(status=1).count()
        report_data['status_2_count'] = publications.filter(status=2).count()
        report_data['status_3_count'] = publications.filter(status=3).count()
        report_data['status_4_count'] = publications.filter(status=4).count()

    return render(request, 'publications/pub_report.html', {
        'years': years,
        'selected_year': selected_year,
        'report_data': report_data,
    })


# Report by year for the model Objection
@login_required
def objection_report(request):
    years = Objection.objects.dates('created_at', 'year').distinct()
    selected_year = request.GET.get('year')

    # Initialize report data
    report_data = {}

    if selected_year:
        # Filter objections for the selected year
        objections = Objection.objects.filter(created_at__year=selected_year)

        # Calculate required metrics
        report_data['total_objections'] = objections.count()
        first_objection = objections.order_by('number').first()  # Get the first objection based on number
        last_objection = objections.order_by('-number').first()  # Get the last objection based on number

        if first_objection:
            report_data['first_objection_number'] = first_objection.number
            report_data['first_objection_date'] = first_objection.created_at

        if last_objection:
            report_data['last_objection_number'] = last_objection.number
            report_data['last_objection_date'] = last_objection.created_at

        # Calculate missing objections
        first_objection_number = report_data.get('first_objection_number')
        last_objection_number = report_data.get('last_objection_number')
        
        report_data['missing_objections'] = []
        if first_objection_number is not None and last_objection_number is not None:
            all_objection_numbers = set(objections.values_list('number', flat=True))
            complete_range = set(range(first_objection_number, last_objection_number + 1))
            report_data['missing_objections'] = list(complete_range - all_objection_numbers)

        report_data['total_missing'] = len(report_data['missing_objections'])
        report_data['formatted_missing_objections'] = format_missing_numbers(sorted(report_data['missing_objections']))
        report_data['total_without_pdf'] = objections.filter(Q(pdf_file__isnull=True) | Q(pdf_file='')).count()
        report_data['total_without_receipt'] = objections.filter(Q(receipt_file__isnull=True) | Q(receipt_file='')).count()

        report_data['total_without_data'] = objections.filter(
            Q(name__isnull=True) | Q(name='') | Q(job__isnull=True) | Q(job='')
        ).count()
        report_data['status_pending_count'] = objections.filter(status=ObjectionStatus.PENDING).count()
        report_data['status_unconfirm_count'] = objections.filter(status=ObjectionStatus.UNCONFIRM).count()
        report_data['status_paid_count'] = objections.filter(status=ObjectionStatus.PAID).count()
        report_data['status_accept_count'] = objections.filter(status=ObjectionStatus.ACCEPT).count()
        report_data['status_reject_count'] = objections.filter(status=ObjectionStatus.REJECT).count()

    return render(request, 'objections/objection_report.html', {
        'years': years,
        'selected_year': selected_year,
        'report_data': report_data,
    })

