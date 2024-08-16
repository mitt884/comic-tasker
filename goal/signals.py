from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Goal
from comic.views import create_comic

@receiver(post_save, sender=Goal)
def create_comic_for_new_goal(sender, instance, created, **kwargs):
    if created:
        create_comic(instance.id)
