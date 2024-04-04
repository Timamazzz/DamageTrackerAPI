from django.urls import path, include
from rest_framework.routers import DefaultRouter

from acts_app.views import ActViewSet, MunicipalityViewSet, BuildingTypeViewSet

router = DefaultRouter()

router.register(r'municipalities', MunicipalityViewSet)
router.register(r'building-types', BuildingTypeViewSet)
router.register(r'', ActViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
