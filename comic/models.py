from django.db import models
#from goal.models import Goal

def get_comic_image_path(instance, filename):
    # Access the goal name through the related comic's goal
    goal_name = instance.comic.goal_id.goal_name
    # This will save images to 'media/comics/<goal_name>/<filename>'
    return f'comics/{goal_name}/{filename}'

class Comic(models.Model):
    #title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    unlocked=models.BooleanField(default=False)
    goal_id=models.ForeignKey('goal.Goal', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"Comic for Goal {self.goal_id.id}"

class Panel(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name='panels')
    image = models.ImageField(upload_to=get_comic_image_path)
    panel_number = models.IntegerField()
    unlocked=models.BooleanField(default=False)

    def __str__(self):
        return f"Panel {self.panel_number} of {self.comic.title}"