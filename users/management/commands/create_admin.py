from django.core.management.base import BaseCommand
from users.models import CustomUser, Role

class Command(BaseCommand):
    help = 'Creates a sample admin user if none exists'

    def handle(self, *args, **kwargs):
        admin_exists = CustomUser.objects.filter(role=Role.ADMIN).exists()
        
        if not admin_exists:
            self.stdout.write("No admin users found. Creating a sample admin user...")
            
            admin_user = CustomUser.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='adminpassword123',
                role=Role.ADMIN,
                is_staff=True,
                is_superuser=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Admin user created successfully: {admin_user.username}"))
            self.stdout.write("Username: admin")
            self.stdout.write("Password: adminpassword123")
            self.stdout.write(self.style.WARNING("Please change this password after first login!"))
        else:
            self.stdout.write(self.style.SUCCESS("Admin user(s) already exist."))