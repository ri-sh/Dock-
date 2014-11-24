from django import forms

class ImageUploadForm(forms.Form):
    """
    Simplest possible form for uploading an image
    """
    image = forms.ImageField()
