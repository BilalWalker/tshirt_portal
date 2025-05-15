from django.db import models
from django.urls import reverse
from django.conf import settings

class DesignStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PUBLISHED = 'PUBLISHED', 'Published'

class Design(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='designs/')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='designs'
    )
    status = models.CharField(
        max_length=10,
        choices=DesignStatus.choices,
        default=DesignStatus.DRAFT
    )
    shopify_product_id = models.CharField(max_length=50, blank=True, null=True)
    shopify_product_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('design_detail', kwargs={'pk': self.pk})
    
    def is_published(self):
        return self.status == DesignStatus.PUBLISHED
