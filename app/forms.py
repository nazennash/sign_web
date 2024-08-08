# forms.py
from django import forms

class VideoUploadForm(forms.Form):
    video = forms.FileField(required=False)
    youtube_url = forms.URLField(required=False, label='YouTube URL')

class ImageUploadForm(forms.Form):
    image = forms.FileField()
