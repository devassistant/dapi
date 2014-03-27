from django.forms import *
from django.contrib.auth.models import User


class UploadDapForm(Form):
    file = FileField()

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
