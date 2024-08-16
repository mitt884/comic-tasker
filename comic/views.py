import os
from goal.models import Goal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from pathlib import Path
from PIL import Image
import fal_client.client
import requests
from io import BytesIO
import google.generativeai as genai
from .models import Comic, Panel
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import traceback
from django.core.files.base import ContentFile
from django.urls import reverse
from mycalendar.models import Events

fal_client = fal_client.client.SyncClient(os.environ['FAL_KEY'])

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_storyline():
    prompt = ("Generate a storyline for a silent 8-panel comic. Provide each panel's description "
          "separately with a clear numbering format like 'Panel 1:', 'Panel 2:', and so on. "
          "The storyline should be funny, with a plot twist, and each panel's description "
          "should be concise and directly related to the storyline.")

    
    response = model.generate_content(prompt)
    return response.text

def split_storyline_into_panels(storyline, panel_count=8):
    panels_prompt = [panel.strip() for panel in storyline.split('Panel ') if panel.strip()]
    return panels_prompt[:panel_count]

def create_comic(goal_id): 
    goal = get_object_or_404(Goal, id=goal_id)
    storyline = generate_storyline()
    panels = split_storyline_into_panels(storyline, 8)
    
    comic = Comic.objects.create(description=storyline, goal_id=goal)
    
    comic_folder = os.path.join(settings.MEDIA_ROOT, 'comics', str(goal.goal_name))
    Path(comic_folder).mkdir(parents=True, exist_ok=True)
    
    storyline_context = ""
    
    for index, panel_prompt in enumerate(panels):
        try:
            combined_prompt = f"Create a Japanese manga style, black and white only, without any dialogue comic panel for the following story: {storyline_context} Now, focus on this scene: {panel_prompt}"
            
            result = fal_client.run(
                "fal-ai/fast-sdxl",
                arguments={
                    "prompt": combined_prompt,
                    "negative_prompt": "western style, realistic, photograph",
                    "steps": 30,
                    "sampler": "DPM++ 2M Karras",
                    "guidance_scale": 7.5
                }
            )
            image_url = result['images'][0]['url']
            print(f"Generated image URL for panel {index + 1}: {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
           
            
            panel = Panel.objects.create(
                comic=comic,
                panel_number=index + 1,
            )
            
            image_name = f'panel_{index + 1}.png'
            panel.image.save(image_name, ContentFile(response.content), save=True)
            
            storyline_context += " " + panel_prompt
            
        except Exception as e:
            print(f"Error generating panel {index + 1}: {str(e)}")
            print(traceback.format_exc())
    
    return comic

def generate_comic_view(request):
    goal_id = request.GET.get('goal_id')
    if not goal_id:
        return JsonResponse({'error': 'Goal ID is required.'}, status=400)

    comic = create_comic(goal_id)
    
    return JsonResponse({
        'comic_id': comic.id,
        'description': comic.description,
        'goal_id': comic.goal_id.id,
        'panels': [{'image': panel.image.url, 'unlocked': panel.unlocked} for panel in comic.panels.all()]
    })


def view_comic(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    comic = get_object_or_404(Comic, goal_id=goal)
    panels = comic.panels.all()
    return render(request, 'view_comic.html', {'comic': comic, 'panels': panels, 'goal': goal})

def mark_task_completed(request, task_id):
    task = get_object_or_404(Events, id=task_id)
    task.completed = True
    task.save()
    comic = task.goal.comic_set.first()
    if comic:
        return redirect(reverse('view_comic', args=[comic.id]))

    return redirect('mark_task_completed') 