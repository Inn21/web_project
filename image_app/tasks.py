from celery import shared_task, current_task
from celery.exceptions import Ignore
from .models import ImageTask
from PIL import Image, ImageFilter
import os

@shared_task(bind=True)
def process_image_task(self, task_id):
    task = ImageTask.objects.get(id=task_id)
    try:
        img = Image.open(task.original_image.path)
        width, height = img.size
        processed_img = Image.new(img.mode, img.size)
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

            processed_img.paste(row, (0, y))

            # Оновлення прогресу
            if (y + 1) % 10 == 0 or y == height - 1:
                self.update_state(state='PROGRESS', meta={'current': y+1, 'total': total_steps})

        # Зберігаємо оброблене зображення
        processed_image_path = task.original_image.path.replace('original_images', 'processed_images')
        processed_img.save(processed_image_path)

        # Оновлюємо модель
        task.processed_image = processed_image_path.replace(task.original_image.storage.location + os.sep, '')
        task.status = 'COMPLETED'
        task.save()
    except Exception as e:
        task.status = 'FAILED'
        task.save()
        raise e