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
         'placeholder': 'Name your project...',
        })



class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ('board','status','completed', 'created_by', 'column','order')

        widgets = {
            'title': forms.TextInput(attrs={
            'class': 'form-control form-control-lg rounded-pill shadow-sm border-light mb-3',
            }),
            'description': forms.Textarea(attrs={
            'class': 'form-control rounded shadow-sm border-light mb-3',
            'rows': 3
            
            }),
           
            'assigned_to': forms.Select(attrs={
            'class': 'form-select form-control-lg rounded-pill shadow-sm border-light mb-3',
           
            }),

            'deadline': forms.DateTimeInput(
                attrs={'type': 'date', 'class': 'form-control form-control-lg rounded-pill shadow-sm border-light mb-3 ',
               
            }),
              'priority': forms.Select(
                attrs={'class': 'form-select form-control-lg rounded-pill shadow-sm border-light mb-3',
               
            }),

         }     


        
    def __init__(self, *args, user=None, board=None, **kwargs):
        super().__init__(*args, **kwargs)
        if board:
            self.fields['assigned_to'].queryset = board.members.all()
       

  

class InviteMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=None,
        label="Select a user to invite"
    )

    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        if board is not None:
            self.fields['user'].queryset = User.objects.exclude(id__in=board.members.values_list('id', flat=True)).exclude(id=board.created_by.id)
            self.fields['user'].widget.attrs.update({
                'class':'form-select form-control-lg rounded-pill text-center shadow-sm border-0',
        
        
        })


class AddColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Column name...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }