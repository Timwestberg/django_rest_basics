"""
Views for the Appointment APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Appointment
from appointment import serializers


class AppointmentViewSets(viewsets.ModelViewSet):
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


