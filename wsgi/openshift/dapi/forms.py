from django import forms


class UploadDapForm(forms.Form):
    file = forms.FileField()
