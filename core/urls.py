"""
URL configuration for the trademarks project.

"""

# Imports of the required python modules and libraries
######################################################
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# URL patterns for the project
##############################
urlpatterns = [
    path('admin/', admin.site.urls),
    path('manage/', include('users.urls')),
    path('', include('documents.urls')),  # Include the documents app URLs
    # path('i18n/setlang/', set_language, name='set_language'),
]

# If the project is in DEBUG mode, serve media files using Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
