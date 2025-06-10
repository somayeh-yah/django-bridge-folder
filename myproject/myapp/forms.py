from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User #här importerar vi vår egna användar modell från models.py
from django.contrib.auth import get_user_model

User = get_user_model() 


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES, 
        required=True,
        label= ""
       
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]
