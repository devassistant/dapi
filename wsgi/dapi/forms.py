from django.forms import *
from dapi.models import MetaDap
from django.contrib.auth.models import User


class UploadDapForm(Form):
    file = FileField()

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class ComaintainersForm(ModelForm):
    class Meta:
        model = MetaDap
        fields = ('comaintainers',)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['comaintainers'].help_text = ''

class DeleteDapForm(Form):
    verification = CharField(max_length=200, help_text='Type the name of this dap to verify the deletion.')

class ActivationDapForm(ModelForm):
    verification = CharField(max_length=200, help_text='Type the name of this dap to verify the deactivation.')

    class Meta:
        model = MetaDap
        fields = ('active',)

class TransferDapForm(ModelForm):
    verification = CharField(max_length=200, help_text='Type the name of this dap to verify the transfer.')

    class Meta:
        model = MetaDap
        fields = ('user',)

