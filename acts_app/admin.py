from django.contrib import admin
from .models import Municipality, BuildingType, Act, DamageType, DamageName, Damage, SignCode


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_victim']


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_at', 'name', 'employee', 'victim', 'municipality', 'address', 'building_type']


@admin.register(DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(DamageName)
class DamageNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']


@admin.register(Damage)
class DamageAdmin(admin.ModelAdmin):
    list_display = ['act', 'damage_type', 'name', 'count', 'note']


@admin.register(SignCode)
class SignCodeAdmin(admin.ModelAdmin):
    list_display = ['act', 'code', 'upd_at', 'is_expired']
    readonly_fields = ['code', 'upd_at', 'is_expired']
