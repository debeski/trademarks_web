from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from .models import Publication

@shared_task
def check_and_update_publication_status():
    """
    Updates the status of publications to 3 if:
    - They were created 30+ days ago
    - They have no linked objections
    - Their status is still 1
    """
    threshold_date = now() - timedelta(days=30)

    affected_rows = Publication.objects.filter(
        created_at__lte=threshold_date,  
        status=1,  
        objection__isnull=True
    ).update(status=3)

    return f"Updated {affected_rows} publications."