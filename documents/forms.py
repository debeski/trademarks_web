# Imports of the required python modules and libraries
######################################################
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div, HTML
from crispy_forms.bootstrap import FormActions
from .models import Decree, Publication, FormPlus, Objection, Country, Government, ComType, DocType, DecreeCategory
import datetime


# Section models forms
######################
class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['en_name', 'ar_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Div(Field('ar_name', css_class='form-control', placeholder="الاسم بالعربية"), css_class='col-md-5'),
                Div(Field('en_name', css_class='form-control', placeholder="الاسم بالانجليزية"), css_class='col-md-5'),
                FormActions(
                    Submit('submit', '{% if id %} حفظ {% else %} اضافة جديد {% endif %}', css_class='btn btn-primary'),
                    HTML(
                        '{% if id %}'
                        ' <a class="btn btn-secondary" href="{% url "manage_sections" %}">الغاء</a>'
                        '{% endif %}'
                    ), css_class='col-md-auto'
                )
            ),
        )

class GovernmentForm(forms.ModelForm):
    class Meta:
        model = Government
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Row(
                Div(Field('name', css_class='form-control', placeholder="اسم النوع"), css_class='col-md-10'),
                FormActions(
                    Submit('submit', '{% if id %} حفظ {% else %} اضافة جديد {% endif %}', css_class='btn btn-primary'),
                    HTML(
                        '{% if id %}'
                        ' <a class="btn btn-secondary" href="{% url "manage_sections" %}">الغاء</a>'
                        '{% endif %}'
                    ), css_class='col-md-auto'
                )
            ),
        )

class ComTypeForm(forms.ModelForm):
    class Meta:
        model = ComType
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Row(
                Div(Field('name', css_class='form-control', placeholder="اسم النوع"), css_class='col-md-10'),
                FormActions(
                    Submit('submit', '{% if id %} حفظ {% else %} اضافة جديد {% endif %}', css_class='btn btn-primary'),
                    HTML(
                        '{% if id %}'
                        ' <a class="btn btn-secondary" href="{% url "manage_sections" %}">الغاء</a>'
                        '{% endif %}'
                    ), css_class='col-md-auto'
                )
            ),
        )

class DocTypeForm(forms.ModelForm):
    class Meta:
        model = DocType
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Row(
                Div(Field('name', css_class='form-control', placeholder="اسم النوع"), css_class='col-md-10'),
                FormActions(
                    Submit('submit', '{% if id %} حفظ {% else %} اضافة جديد {% endif %}', css_class='btn btn-primary'),
                    HTML(
                        '{% if id %}'
                        ' <a class="btn btn-secondary" href="{% url "manage_sections" %}">الغاء</a>'
                        '{% endif %}'
                    ), css_class='col-md-auto'
                )
            ),
        )

class DecreeCategoryForm(forms.ModelForm):
    class Meta:
        model = DecreeCategory
        fields = ['number', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Row(
                Div(Field('number', css_class='form-control', placeholder="رقم الفئة"), css_class='col-md-5'),
                Div(Field('name', css_class='form-control', placeholder="اسم الفئة"), css_class='col-md-5'),
                FormActions(
                    Submit('submit', '{% if id %} حفظ {% else %} اضافة جديد {% endif %}', css_class='btn btn-primary'),
                    HTML(
                        '{% if id %}'
                        ' <a class="btn btn-secondary" href="{% url "manage_sections" %}">الغاء</a>'
                        '{% endif %}'
                    ), css_class='col-md-auto'
                )
            ),
        )


# Primary models forms
######################
class DecreeForm(forms.ModelForm):
    
    category = forms.IntegerField(
        required=False,
        min_value=1, max_value=45,
        label="الفئة",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    # Hidden fields
    is_withdrawn = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    is_canceled = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)

    # Decree number field for autocomplete
    number_canceled = forms.CharField(
        required=False,
        label="رقم القرار المسحوب او الملغي",
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'id': 'id_number_canceled'})
    )
    class Meta:
        model = Decree
        # List the fields you want to include in the form
        fields = [
            'number', 'date', 'status', 'applicant', 'company', 'country',
            'date_applied', 'number_applied', 'ar_brand', 'en_brand',
            'category', 'pdf_file', 'attach', 'notes', 'number_canceled'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize the crispy helper
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.form_class = 'w-75 mx-auto'
        self.fields['status'].empty_label = None
        self.fields['pdf_file'].widget.attrs.update({
            'accept': '.pdf'
        })
        self.fields['attach'].widget.attrs.update({
            'accept': '.pdf'
        })
        self.helper.layout = Layout(
            Div(
                Div(Field('number', css_class='form-control'), css_class='col'),
                Div(Field('date', css_class='form-control flatpickr'), css_class='col'),
                Div(Field('status', css_class='form-control'), css_class='col'),
                HTML("<hr>"),
                Div(Field('applicant', css_class='form-control'), css_class='col'),
                Div(Field('company', css_class='form-control'), css_class='col'),
                Div(Field('country', css_class='form-control'), css_class='col'),
                Div(Field('date_applied', css_class='form-control flatpickr'), css_class='col'),
                Div(Field('number_applied', css_class='form-control'), css_class='col'),
                Div(Field('ar_brand', css_class='form-control'), css_class='col'),
                Div(Field('en_brand', css_class='form-control'), css_class='col'),
                Div(Field('category', css_class='form-control'), css_class='col'),
                css_class='col'
            ),
            # Add the hidden fields
            Field('is_withdrawn', type="hidden"),
            Field('is_canceled', type="hidden"),
            Field('number_canceled', css_class='form-control'),
            HTML("<hr>"),
            Field('pdf_file'),
            Field('attach'),
            Field('notes', rows="2"),
            FormActions(
                Submit('submit', 'حفظ', css_class='btn btn-primary'),
                HTML('<a class="btn btn-secondary" href="{% url \'decree_list\' %}">إلغاء</a>')
            )
        )

    def clean_category(self):
        category = self.cleaned_data.get("category")
        
        # Check if category has a value
        if category:
            try:
                return DecreeCategory.objects.get(number=category)
            except DecreeCategory.DoesNotExist:
                raise forms.ValidationError("Invalid category. Please enter a valid category number.")
        
        # If no category is provided, return it as is
        return category

    def clean_number_canceled(self):
        return self.cleaned_data.get("number_canceled")

class PublicationForm(forms.ModelForm):
    # Extra field to filter decrees by year
    year = forms.CharField(label="سنة القرار", initial=str(datetime.datetime.now().year))
    # For the decree field, we use a ModelChoiceField; its widget will be enhanced by JavaScript.
    decree_number = forms.CharField(
        label="رقم القرار",
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'id': 'id_decree_autocomplete'})
    )
    category = forms.IntegerField(
        required=False,
        min_value=1, max_value=45,
        label="الفئة",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Publication
        fields = [
            'year', 'number', 'decree_number',
            'applicant', 'owner', 'country',
            'address', 'date_applied', 'number_applied',
            'ar_brand', 'en_brand', 'category',
            'img_file', 'attach', 'e_number',
            'is_hidden', 'notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.fields['attach'].widget.attrs.update({
            'accept': '.pdf'
        })
        self.helper.layout = Layout(
            Row(
                Div(Field('year', css_class='form-control'), css_class='col-md-3'),
                Div(Field('decree_number', css_class='form-control', placeholder="اكتب رقم القرار للبحث"), css_class='col-md-9'),
                css_class='form-row'
            ),
            HTML("<hr>"),
            Div(
                Div(Field('number', css_class='form-control'), css_class='col'),
                Div(Field('applicant', css_class='form-control'), css_class='col'),
                Div(Field('owner', css_class='form-control'), css_class='col'),
                Div(Field('country', css_class='form-control'), css_class='col'),
                Div(Field('address', css_class='form-control'), css_class='col'),
                Div(Field('date_applied', css_class='form-control flatpickr'), css_class='col'),
                Div(Field('number_applied', css_class='form-control'), css_class='col'),
                Div(Field('ar_brand', css_class='form-control'), css_class='col'),
                Div(Field('en_brand', css_class='form-control'), css_class='col'),
                Div(Field('category', css_class='form-control'), css_class='col'),
                css_class='col'
            ),
            HTML("<hr>"),
            Field('img_file'),
            Field('attach'),
            HTML("<hr>"),
            Div(
                Div(Field('e_number', css_class='form-control'), css_class='col'),
                Div(Field('notes', css_class='form-control', rows="2"), css_class='col'),
                css_class='col'
            ),

            FormActions(
                Submit('submit', 'حفظ', css_class='btn btn-primary'),
                HTML('<a class="btn btn-secondary" href="{% url \'publication_list\' %}">إلغاء</a>')
            )
        )

class ObjectionForm(forms.ModelForm):
    year = forms.CharField(required=False, label="سنة الإشهار", initial=str(datetime.datetime.now().year))
    pub_number = forms.CharField(
        required=True,
        label="رقم الإشهار",
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'id': 'id_pub_autocomplete',
            'pattern': '^[0-9]+$',  # only numbers
            'title': 'يرجى اختيار رقم اشهار صالح.'
        })
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="تفاصيل"
    )
    pub_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Objection
        fields = [
            'year', 'pub_number', 'pub_id', 'name', 'job', 'nationality', 'address', 'phone',
            'com_name', 'com_job', 'com_address', 'com_og_address', 'com_mail_address',
            'is_paid', 'receipt_file', 'pdf_file', 'notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.fields['receipt_file'].required = False
        self.fields['pdf_file'].widget.attrs.update({
            'accept': '.pdf'
        })

class ObjectionPubPickForm(forms.ModelForm):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="تفاصيل"
    )
    # pub_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Objection
        fields = [
            'name', 'job', 'nationality', 'address', 'phone',
            'com_name', 'com_job', 'com_address', 'com_og_address', 'com_mail_address',
            'is_paid', 'receipt_file', 'pdf_file', 'notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.fields['receipt_file'].required = False
        self.fields['pdf_file'].widget.attrs.update({
            'accept': '.pdf'
        })

class FormPlusForm(forms.ModelForm):
    class Meta:
        model = FormPlus
        fields = ['type', 'number', 'date', 'government', 'title', 'keywords', 'pdf_file', 'word_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.form_class = 'w-75 mx-auto'
        self.fields['pdf_file'].widget.attrs.update({
            'accept': '.pdf'
        })
        # Override the widget for the word_file field to accept only Word files
        self.fields['word_file'].widget.attrs.update({
            'accept': '.doc,.docx'
        })
        self.helper.layout = Layout(
            Div(
                Div(Field('type', css_class='form-control'), css_class='col'),
                Div(Field('number', css_class='form-control'), css_class='col'),
                Div(Field('date', css_class='form-control flatpickr'), css_class='col'),
                Div(Field('government', css_class='form-control'), css_class='col'),
                Div(Field('title', css_class='form-control'), css_class='col'),
                Div(Field('keywords', css_class='form-control', rows="3"), css_class='col'),
                css_class='col'
            ),
            Field('pdf_file'),
            Field('word_file'),
            FormActions(
                Submit('submit', 'حفظ', css_class='btn btn-primary'),
                HTML('<a class="btn btn-secondary" href="{% url \'formplus_list\' %}">إلغاء</a>')
            )
        )
