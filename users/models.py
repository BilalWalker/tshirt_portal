from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Role(models.TextChoices):
    ADMIN = 'ADMIN', _('Admin')
    DESIGNER = 'DESIGNER', _('Designer')
    VIEWER = 'VIEWER', _('Viewer')

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.DESIGNER,
    )
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == Role.ADMIN
    
    def is_designer(self):
        return self.role == Role.DESIGNER or self.role == Role.ADMIN