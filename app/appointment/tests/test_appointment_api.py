"""
Tests for appointment APIs.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Appointment

from appointment.serializers import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
)

APPOINTMENT_URL = reverse('appointment:appointment-list')


def detail_url(appointment_id):
    """Create and return appointment detail URL."""
    return reverse('appointment:appointment-detail', args=[appointment_id])


def create_appointment(user, **params):
    """Create and return a sample Appointment"""
    defaults = {
        'title': 'Sample Appointment Title',
        'time_minutes': 25,
        'price': Decimal('5.25'),
        'description': 'Sample Appointment Description',
        'link': 'https://example.com/appointment.pdf',
    }
    defaults.update(params)

    appointment = Appointment.objects.create(user=user, **defaults)
    return appointment


class PublicAppointmentAPITests(TestCase):
    """Test unauthorized API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(APPOINTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAppointmentApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_appointments(self):
        """Test retrieving a list of Appointments."""
        create_appointment(user=self.user)
        create_appointment(user=self.user)

        res = self.client.get(APPOINTMENT_URL)

        appointments = Appointment.objects.all().order_by('-id')
        serializer = AppointmentSerializer(appointments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_appointment_list_limited_to_user(self):
        """Test list of appointments is linited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_appointment(user=other_user)
        create_appointment(user=other_user)

        res = self.client.get(APPOINTMENT_URL)

        appointments = Appointment.objects.filter(user=self.user)
        serializer = AppointmentSerializer(appointments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_appointment_detail(self):
        """Test get appointment detail."""
        appointment = create_appointment(user=self.user)

        url = detail_url(appointment.id)
        res = self.client.get(url)

        serializer = AppointmentDetailSerializer(appointment)
        self.assertEqual(res.data, serializer.data)
