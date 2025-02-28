from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser with predefined credentials'

    def handle(self, *args, **kwargs):
        User = get_user_model()  # Get the custom user model
        username = 'admin'
        email = 'admin@example.com'
        password = 'db123123'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with username: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser with username {username} already exists'))
