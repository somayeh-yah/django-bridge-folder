from django import forms
from .models import *

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields =  ['name']

     

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.fields['name'].widget.attrs.update({
        'class':'form-control form-control-lg rounded-pill text-center shadow-sm border-0',
         'placeholder': 'enter your board name...',
        })



class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ('board','status')


