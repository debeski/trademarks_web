from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'

    def ready(self):
        """ Override Permission model's __str__ method after apps are ready """
        from django.contrib.auth.models import Permission

        def custom_permission_str(self):
            """ Custom Arabic translations for Django permissions """
            model_name = str(self.content_type)
            permission_name = str(self.name)

            # Translate default permissions
            if "Can add" in permission_name:
                permission_name = permission_name.replace("Can add", " إضافة ")
            elif "Can change" in permission_name:
                permission_name = permission_name.replace("Can change", " تعديل ")
            elif "Can delete" in permission_name:
                permission_name = permission_name.replace("Can delete", " حذف ")
            elif "Can view" in permission_name:
                permission_name = permission_name.replace("Can view", " عرض ")

            return f"{model_name} - {permission_name}"

        # Override the __str__ method
        Permission.__str__ = custom_permission_str
