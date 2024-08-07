# forms.py
from django import forms

class VideoUploadForm(forms.Form):
    video = forms.FileField()

class ImageUploadForm(forms.Form):
    image = forms.FileField()
