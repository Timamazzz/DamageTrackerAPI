from django.contrib import admin
from .models import Municipality, BuildingType, Act, DamageType, Damage, ActSign, Address
from django.contrib import messages
import pandas as pd
from django.http import HttpResponse


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_victim']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['name', 'fias_id']


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ['number', 'created_at', 'employee', 'victim', 'municipality', 'address', 'building_type']
    list_filter = ['created_at']

    actions = ['export_acts_to_excel']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if request.user.is_staff:
            if not request.user.municipality:
                self.message_user(request, "У вас не указан муниципалитет.", level=messages.WARNING)
                return qs.none()

            user_municipality = request.user.municipality
            filtered_qs = qs.filter(municipality=user_municipality) | qs.filter(employee=request.user)

            if not filtered_qs.exists():
                self.message_user(request, "Актов нет.", level=messages.INFO)
                return qs.none()

            return filtered_qs

        self.message_user(request, "У вас нет доступа к актам.", level=messages.ERROR)
        return qs.none()

    def export_acts_to_excel(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Нет актов для экспорта.", level=messages.ERROR)
            return

        data = []
        for act in queryset:
            data.append({
                'Номер': act.number,
                'Дата создания': act.created_at.strftime("%d.%m.%Y %H:%M"),
                'Сотрудник': str(act.employee),
                'Пострадавший': str(act.victim) if act.victim else '',
                'Муниципалитет': str(act.municipality),
                'Адрес': str(act.address),
                'Тип постройки': str(act.building_type),
                'Время подписания': act.signed_at.strftime("%d.%m.%Y %H:%M") if act.signed_at else '',
            })

        df = pd.DataFrame(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=acts.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Акты')

        return response

    export_acts_to_excel.short_description = "Экспортировать в Excel"


@admin.register(DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Damage)
class DamageAdmin(admin.ModelAdmin):
    list_display = ['act', 'damage_type', 'count', 'note']


@admin.register(ActSign)
class SignCodeAdmin(admin.ModelAdmin):
    list_display = ['act', 'code', 'upd_at', 'is_expired']
    readonly_fields = ['code', 'upd_at', 'is_expired']
