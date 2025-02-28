import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import UserActivityLog

User = get_user_model()  # Use custom user model

class UserTable(tables.Table):
    username = tables.Column(verbose_name="اسم المستخدم")
    email = tables.Column(verbose_name="البريد الالكتروني")
    full_name = tables.Column(verbose_name="الاسم الكامل")
    # is_staff = tables.Column(verbose_name="مدير")

    # Action buttons for edit and delete (summoned column)
    actions = tables.TemplateColumn(
        '<a href="{% url "edit_user" record.id %}" class="btn btn-info btn-sm">Edit</a> '
        ' {% if user.is_superuser %} <button type="button" class="btn btn-danger btn-sm" data-bs-toggle="modal" data-bs-target="#deleteModal{{ record.id }}">Delete</button>{% endif %}',
        orderable=False, 
        verbose_name=''
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap5.html"
        fields = ("full_name", "username", "email", "phone", "occupation", "is_staff", "actions")

class UserActivityLogTable(tables.Table):
    class Meta:
        model = UserActivityLog
        template_name = "django_tables2/bootstrap5.html"
        fields = ("timestamp", "user", "action", "model_name", "object_id", "number", "ip_address")

