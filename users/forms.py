from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms

UserModel = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserModel
        # Define fields editable when changing user info
        fields = ('username', 'email', 'first_name', 'last_name') 


class UserUpdateForm(forms.ModelForm):
    

    class Meta:
        model = UserModel
        
        fields = ('username', 'email', 'first_name', 'last_name') 