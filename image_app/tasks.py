from celery import shared_task, current_task
from celery.exceptions import Ignore
from image_processing_project import settings
from .models import ImageTask
from PIL import  Image, ImageFilter, ImageOps, ImageEnhance
import os


@shared_task(bind=True)
def process_image_task(self, task_id):
    task = ImageTask.objects.get(id=task_id)
    try:
        img = Image.open(task.original_image.path)
        width, height = img.size
        processed_img = Image.new(img.mode, img.size)      

        thumbnail_size = (300, 300)  # Розмір зменшеної копії
        
        compressed_image = Image.open(task.original_image.path)
        compressed_image.thumbnail(thumbnail_size)

        # Визначаємо шлях для збереження компресованого зображення
        compressed_image_relative_path = os.path.join('original_images', 'compressed', os.path.basename(task.original_image.name))
        compressed_image_full_path = os.path.join(settings.MEDIA_ROOT, compressed_image_relative_path)

        # Створюємо директорію, якщо її немає
        os.makedirs(os.path.dirname(compressed_image_full_path), exist_ok=True)

        # Зберігаємо компресоване зображення
        compressed_image.save(compressed_image_full_path)

        # Оновлюємо модель
        task.original_image_compressed.name = compressed_image_relative_path
        # Решта оновлень полів моделі...
        task.save()

        total_steps = height


        for y in range(height):
            # Перевірка на відміну задачі
            task.refresh_from_db()
            if task.cancelled:
                # Завершуємо задачу
                self.update_state(state='REVOKED')
                raise Ignore()

            # Обробка рядка
            row = img.crop((0, y, width, y+1))
            if task.operation == 'grayscale':
                row = row.convert('L') 
            elif task.operation == 'blur':
                row = row.filter(ImageFilter.BLUR)
            elif task.operation == 'invert':
                row = ImageOps.invert(row) 
            elif task.operation == 'contrast':
                enhancer = ImageEnhance.Contrast(row)
                row = enhancer.enhance(2)  
            elif task.operation == 'sharpen':
                row = row.filter(ImageFilter.SHARPEN)

            processed_img.paste(row, (0, y))

            # Оновлення прогресу
            if (y + 1) % 10 == 0 or y == height - 1:
                self.update_state(state='PROGRESS', meta={'current': y+1, 'total': total_steps})

        # Зберігаємо оброблене зображення
        processed_image_path = task.original_image.path.replace('original_images', 'processed_images')
        processed_img.save(processed_image_path)

        # Генеруємо зменшену копію для попереднього перегляду
        thumbnail_img = processed_img.copy()
        thumbnail_img.thumbnail(thumbnail_size)
        thumbnail_image_path = processed_image_path.replace('processed_images', 'thumbnails')
        os.makedirs(os.path.dirname(thumbnail_image_path), exist_ok=True)
        thumbnail_img.save(thumbnail_image_path)

        # Оновлюємо модель
        task.processed_image = processed_image_path.replace(task.original_image.storage.location + os.sep, '')
        task.thumbnail_image = thumbnail_image_path.replace(task.original_image.storage.location + os.sep, '')
        task.status = 'COMPLETED'
        task.save()
    except Exception as e:
        task.status = 'FAILED'
        task.save()
        raise e