"""
URL mappings for the appointment app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from appointment import views

router = DefaultRouter()
router.register('appointments', views.AppointmentViewSets)

app_name = 'appointment'

urlpatterns = [
    path("", include(router.urls))
]
