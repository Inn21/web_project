# image_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import ImageTask
from .tasks import process_image_task
from celery.result import AsyncResult
from django.shortcuts import get_object_or_404

def signup_view(request):
    from django.contrib.auth.forms import UserCreationForm
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_task = form.save(commit=False)
            image_task.user = request.user
            image_task.status = 'PROCESSING'
            image_task.save()

            # Запускаємо задачу та зберігаємо task_id
            task = process_image_task.delay(image_task.id)
            image_task.celery_task_id = task.id
            image_task.save()

            return redirect('task_status', task_id=image_task.id)
    else:
        form = ImageUploadForm()
    return render(request, 'image_app/upload.html', {'form': form})

@login_required
def task_status(request, task_id):
    task = ImageTask.objects.get(id=task_id, user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {
            'status': task.status,
        }
        if task.status == 'COMPLETED':
            response_data['thumbnail_image_url'] = task.thumbnail_image.url if task.thumbnail_image else ''
            response_data['processed_image_url'] = task.processed_image.url if task.processed_image else ''
        elif task.status == 'FAILED':
            response_data['error'] = 'Задача завершилася з помилкою.'
        elif task.status == 'CANCELLED':
            response_data['error'] = 'Задачу було відмінено.'
        else:
            result = AsyncResult(task.celery_task_id)
            if result.state == 'PROGRESS':
                response_data['progress'] = result.info.get('current', 0)
                response_data['total'] = result.info.get('total', 1)
        return JsonResponse(response_data)
    return render(request, 'image_app/task_status.html', {'task': task})

@login_required
def cancel_task(request, task_id):
    if request.method == 'POST':
        image_task = get_object_or_404(ImageTask, id=task_id, user=request.user)
        if image_task.status in ['PROCESSING', 'PENDING']:
            # Встановлюємо прапорець відміни
            image_task.cancelled = True
            image_task.status = 'CANCELLED'
            image_task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Неможливо відмінити задачу'})
    else:
        return JsonResponse({'success': False, 'message': 'Неправильний метод запиту'})
@login_required
def task_history(request):
    tasks = ImageTask.objects.filter(user=request.user).order_by('-created_at')    
    return render(request, 'image_app/task_history.html', {'tasks': tasks})