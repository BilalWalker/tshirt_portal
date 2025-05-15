from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Import here to avoid circular imports
        from django.core.management import call_command
        from django.db.models.signals import post_migrate
        
        def create_admin_user(sender, **kwargs):
            if sender.name == self.name:
                call_command('create_admin')
        
        post_migrate.connect(create_admin_user, sender=self)