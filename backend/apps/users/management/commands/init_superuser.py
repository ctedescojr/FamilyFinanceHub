from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Default credentials
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
        
        # Check if ANY superuser exists
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('No superuser found. Creating one...')
            try:
                # Check if a user with this specific email already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.WARNING(f'User with email {email} already exists. Skipping creation.'))
                    return

                # Create the superuser
                User.objects.create_superuser(
                    username='admin', # Providing a default username
                    email=email,
                    password=password,
                    first_name='Admin',
                    last_name='System',
                    family_role='FATHER' # Required by your custom model choices
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Superuser created successfully!'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
                self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'❌ Error creating superuser: {e}'))
        else:
            self.stdout.write('Superuser already exists. Skipping creation.')
