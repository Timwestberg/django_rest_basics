"""
Serializer for Appointment APIs
"""
from rest_framework import serializers

from core.models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments."""

    class Meta:
        model = Appointment
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class AppointmentDetailSerializer(AppointmentSerializer):
    """Serializer for appointment details view."""

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields = ['description']
