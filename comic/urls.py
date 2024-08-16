from django.urls import path
from .views import generate_comic_view, view_comic, mark_task_completed

urlpatterns = [
    path('generate-comic/', generate_comic_view, name='generate_comic'),
    path('view-comic/<int:goal_id>/', view_comic, name='view_comic'),
    path('mark_task_completed/<int:task_id>/', mark_task_completed, name='mark_task_completed'),
]