from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ThemePreference


class UserSignupForm(UserCreationForm):
    """Extended user creation form with email field."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'accept': 'image/*',
        'class': 'form-control'
    }))

    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'theme']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['theme'].queryset = ThemePreference.objects.all()
        self.fields['theme'].empty_label = None
