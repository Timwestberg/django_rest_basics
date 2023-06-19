"""
Serializer for Appointment APIs
"""
from rest_framework import serializers

from core.models import Appointment, Language


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for languages"""

    class Meta:
        model = Language
        fields = ['id', 'name']
        read_only_fields = ['id']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments."""
    languages = LanguageSerializer(many=True, required=False)

    class Meta:
        model = Appointment
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'languages']
        read_only_fields = ['id']

    def _get_or_create_languages(self, languages, appointment):
        """Handle getting or creating Languages as needed."""
        auth_user = self.context['request'].user
        for language in languages:
            language_obj, created = Language.objects.get_or_create(
                user=auth_user,
                **language,
            )
            appointment.languages.add(language_obj)



    def create(self, validated_data):
        """Create an appointment."""
        languages = validated_data.pop('languages', [])
        appointment = Appointment.objects.create(**validated_data)
        self._get_or_create_languages(languages, appointment)

        return appointment

    def update(self, instance, validated_data):
        """Update Appointment"""
        languages = validated_data.pop('languages', None)
        if languages is not None:
            instance.languages.clear()
            self._get_or_create_languages(languages, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class AppointmentDetailSerializer(AppointmentSerializer):
    """Serializer for appointment details view."""

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ['description']

