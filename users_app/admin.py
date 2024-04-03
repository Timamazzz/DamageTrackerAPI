from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ActivationCode, Position, User
from django import forms


class CustomUserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(label="Номер телефона", widget=forms.PasswordInput)
    password1 = forms.CharField(label='Пароль', required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone_number', 'password1', 'password2', 'is_employee']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_employee', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Work info', {'fields': ('position', 'workplace')}),
    )
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'upd_at')
    search_fields = ('user__phone_number', 'code')
    ordering = ('user__phone_number',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)
