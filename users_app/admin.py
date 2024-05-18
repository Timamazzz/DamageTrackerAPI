from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ActivationCode, Position, User
from django import forms


class CustomUserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(label="Номер телефона", widget=forms.TextInput())
    password1 = forms.CharField(label='Пароль', required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone_number', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"] if self.cleaned_data["password1"] else None
        user.set_password(password)
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "password1", "password2"),
            },
        ),
    )
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'patronymic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Work info', {'fields': ('position', 'workplace', 'municipality')}),
    )
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.pk)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and request.user == obj:
            return True
        return False


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
