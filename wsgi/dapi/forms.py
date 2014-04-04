from django.forms import *
from dapi.models import MetaDap, Report
from django.contrib.auth.models import User

VERIFY_HELP_TEXT = 'Type the {what} of this dap to verify the {why}.'


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
    verification = CharField(max_length=200, help_text=VERIFY_HELP_TEXT.format(what='name', why='deletion'))


class DeleteVersionForm(Form):
    verification_name = CharField(max_length=200, help_text=VERIFY_HELP_TEXT.format(what='name', why='deletion'))
    verification_version = CharField(max_length=200, help_text=VERIFY_HELP_TEXT.format(what='version', why='deletion'))


class ActivationDapForm(ModelForm):
    verification = CharField(max_length=200, help_text=VERIFY_HELP_TEXT.format(what='name', why='deactivation'))

    class Meta:
        model = MetaDap
        fields = ('active',)


class TransferDapForm(ModelForm):
    verification = CharField(max_length=200, help_text='Type the name of this dap to verify the transfer.')

    class Meta:
        model = MetaDap
        fields = ('user',)


class LeaveDapForm(Form):
    verification = CharField(max_length=200, help_text='Type the name of this dap to verify the leaving.')


class TagsForm(ModelForm):

    class Meta:
        model = MetaDap
        fields = ('tags',)


class ReportForm(ModelForm):

    class Meta:
        model = Report
        fields = ('problem', 'versions', 'message')
        help_texts = {
            'problem': 'Select the type of problem you want to report.',
            'versions': 'Where this problem occurs? If you are not sure, you can leave it blank.',
            'message': 'Describe the problem you want to report.',
        }


class ReportAnonymousForm(ModelForm):

    class Meta(ReportForm.Meta):
        fields = ReportForm.Meta.fields + ('email',)
        help_texts = ReportForm.Meta.help_texts
        help_texts['email'] = 'Optional. So we can inform you about the solution. We don\'t send spam or sell e-mail addresses.'
