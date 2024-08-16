from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Events
from comic.models import Panel
@receiver(post_save, sender=Events)
def unlock_comic_panel(sender, instance, **kwargs):
    if instance.completed:
        comic = instance.goal.comic_set.first()
        if comic:
            total_tasks = instance.goal.taskbyai_set.count()
            completed_tasks = instance.goal.events_set.filter(completed=True).count()
            total_panels = comic.panels.count()
            if completed_tasks == total_tasks:
                remaining_locked_panels = comic.panels.filter(unlocked=False)
                for panel in remaining_locked_panels:
                    panel.unlocked = True
                    panel.save()
            else:
                if completed_tasks <= total_panels:
                    panel_to_unlock = comic.panels.filter(unlocked=False).first()
                    if panel_to_unlock:
                        panel_to_unlock.unlocked = True
                        panel_to_unlock.save()




