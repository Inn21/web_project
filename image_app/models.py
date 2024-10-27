# image_app/models.py

from django.db import models
from django.contrib.auth.models import User

class ImageTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    OPERATION_CHOICES = [
        ('grayscale', 'Grayscale'),
        ('blur', 'Blur'),
        ('invert', 'Invert Colors'),
        ('contrast', 'Increase Contrast'),
        ('sharpen', 'Sharpen'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='original_images/')
    original_image_compressed = models.ImageField(upload_to='original_images/compressed', null=True, blank=True)

    processed_image = models.ImageField(upload_to='processed_images/', null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnails/', null=True, blank=True) 
    
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, default='grayscale')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    celery_task_id = models.CharField(max_length=50, null=True, blank=True)
    cancelled = models.BooleanField(default=False)


    def __str__(self):
        return f"Task {self.id} - {self.operation}"
