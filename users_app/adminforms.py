from django import forms
from users_app.models import User


class CustomUserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(label="Номер телефона", widget=forms.TextInput())
    password1 = forms.CharField(label='Пароль', required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone_number', 'password1']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"] if self.cleaned_data["password1"] else None
        user.set_password(password)
        if commit:
            user.save()
        return user
