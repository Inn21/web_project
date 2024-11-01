# Generated by Django 5.1.2 on 2024-10-27 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagetask',
            name='celery_task_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imagetask',
            name='operation',
            field=models.CharField(choices=[('grayscale', 'Grayscale'), ('blur', 'Blur')], default='grayscale', max_length=20),
        ),
        migrations.AlterField(
            model_name='imagetask',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=10),
        ),
    ]
