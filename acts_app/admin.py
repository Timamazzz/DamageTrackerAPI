from django.contrib import admin
from .models import Municipality, BuildingType, Act, DamageType, Damage, ActSign, Address


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if request.user.is_staff:
            if not request.user.municipality:
                self.message_user(request, "У вас не указан муниципалитет.", level='error')
                return qs.none()

            user_municipality = request.user.municipality
            filtered_qs = qs.filter(municipality=user_municipality) | qs.filter(employee=request.user)

            if not filtered_qs.exists():
                self.message_user(request, "Актов нет.", level='info')
                return qs.none()

            return filtered_qs

        self.message_user(request, "У вас нет доступа к актам.", level='error')
        return qs.none()


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
