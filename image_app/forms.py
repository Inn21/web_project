# image_app/forms.py

from django import forms
from .models import ImageTask

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageTask
        fields = ['original_image', 'operation']
        widgets = {
            'operation': forms.Select(choices=[
                ('grayscale', 'Grayscale'),
                ('blur', 'Blur'),
                # Додайте інші операції, якщо потрібно
            ]),
        }
