from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'role', 'level', 'bio', 'city',
            'technologies', 'github_profile', 'telegram',
            'looking_for', 'work_mode', 'experience_years',
            'avatar'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'technologies': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Python, Django, JavaScript, React, Docker...'
            }),
        }


