"""
Views for the Appointment APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Appointment, Language
from appointment import serializers


class AppointmentViewSet(viewsets.ModelViewSet):
    """View for Manage Appointment APIs"""
    serializer_class = serializers.AppointmentDetailSerializer
    queryset = Appointment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve appointments for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.AppointmentSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new appointment"""
        serializer.save(user=self.request.user)


class LanguageViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Manage Languages in the database."""
    serializer_class = serializers.LanguageSerializer
    queryset = Language.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')



