# Generated by Django 5.1.2 on 2024-10-27 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_app', '0005_imagetask_original_image_compressed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagetask',
            name='operation',
            field=models.CharField(choices=[('grayscale', 'Grayscale'), ('blur', 'Blur'), ('invert', 'Invert Colors'), ('contrast', 'Increase Contrast'), ('sharpen', 'Sharpen')], default='grayscale', max_length=20),
        ),
    ]
