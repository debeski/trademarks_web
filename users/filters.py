import django_filters
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, HTML, Div
from django.db.models import Q

User = get_user_model()  # Use custom user model

class UserFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(
        method='filter_keyword',
        label='',
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone", "occupation"]  # Include phone and occupation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'GET'
        self.form.helper.form_class = 'form-inline'
        self.form.helper.form_show_labels = False
        self.form.helper.layout = Layout(
            Row(
                Column(Field('keyword', placeholder="البحث"), css_class='form-group col-md-6'),
                Column(Submit('submit', 'بحث', css_class='btn btn-secondary w-100'), css_class='form-group col-md-auto text-center'),
                Column(HTML('{% if request.GET and request.GET.keys|length > 1 %} <a href="{% url "manage_users" %}" class="btn btn-warning">clear</a> {% endif %}'), css_class='form-group col-md-auto text-center'),
                css_class='form-row'
            ),
        )

    def filter_keyword(self, queryset, name, value):
        """
        Filter the queryset by matching the keyword in username, email, phone, and occupation.
        """
        q = Q(username__icontains=value) | Q(email__icontains=value) | Q(phone__icontains=value) | Q(occupation__icontains=value)
        return queryset.filter(q)
