from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ActivationCode, Position, User
from django import forms


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number', 'password', 'is_employee')


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
