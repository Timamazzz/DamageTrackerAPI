from django.contrib import admin
from .models import DamageImage, ActImage


@admin.register(DamageImage)
class DamageImageAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'act', 'upload_time')
    search_fields = ('original_name', )
    ordering = ('upload_time',)


@admin.register(ActImage)
class ActImageAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'act', 'upload_time')
    search_fields = ('original_name', 'act__number')
    ordering = ('upload_time',)
