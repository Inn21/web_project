from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('task/<int:task_id>/', views.task_status, name='task_status'),
    path('history/', views.task_history, name='task_history'),
    path('cancel_task/<int:task_id>/', views.cancel_task, name='cancel_task'),
]
