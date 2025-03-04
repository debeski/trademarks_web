# Imports of the required python modules and libraries
######################################################
import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import UserActivityLog

User = get_user_model()  # Use custom user model

class UserTable(tables.Table):
    username = tables.Column(verbose_name="اسم المستخدم")
    email = tables.Column(verbose_name="البريد الالكتروني")
    full_name = tables.Column(verbose_name="الاسم بالكامل", orderable=False,)

    # Action buttons for edit and delete (summoned column)
    actions = tables.TemplateColumn(
        template_name='users/user_actions.html',
        orderable=False,
        verbose_name=''
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap5.html"
        fields = ("username", "email", "full_name", "phone", "occupation", "is_staff", "actions")

class UserActivityLogTable(tables.Table):
    class Meta:
        model = UserActivityLog
        template_name = "django_tables2/bootstrap5.html"
        fields = ("timestamp", "user", "action", "model_name", "object_id", "number", "ip_address")

