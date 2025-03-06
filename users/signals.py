# Imports of the required python modules and libraries
######################################################
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from .models import UserActivityLog
import threading
from django.contrib.auth.signals import user_logged_in, user_logged_out

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Log user login actions."""
    UserActivityLog.objects.create(
        user=user,
        action="LOGIN",
        model_name="مصادقة",
        object_id=None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        timestamp=now(),
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log user logout actions."""
    UserActivityLog.objects.create(
        user=user,
        action="LOGOUT",
        model_name="مصادقة",
        object_id=None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        timestamp=now(),
    )

def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip