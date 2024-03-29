from django.contrib import admin
from .models import Position, Employee, ActivationCode


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'phone_number', 'position']


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ['employee', 'code', 'created_at', 'is_expired']
