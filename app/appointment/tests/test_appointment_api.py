"""
Tests for appointment APIs.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Appointment,
    Language
)

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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
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
        other_user = create_user(
            email='other@example.com',
            password='password123',
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

    def test_create_appointment(self):
        """Test creating an appointment."""
        payload = {
            'title': 'Sample Appointment Title',
            'time_minutes': 25,
            'price': Decimal('5.25'),
        }

        res = self.client.post(APPOINTMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(appointment, k), v)
        self.assertEqual(appointment.user, self.user)

    def test_partial_update(self):
        """Test partial update of an appointment."""
        original_link = 'https://example.com/appointment.pdf'
        appointment = create_appointment(
            user=self.user,
            title='Sample Appointment Title',
            link=original_link,
        )

        payload = {
            'title': 'New Appointment Title'
        }
        url = detail_url(appointment.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.title, payload['title'])
        self.assertEqual(appointment.link, original_link)

    def test_full_update(self):
        """Test full update of an appointment."""
        appointment = create_appointment(
            user=self.user,
            title='Sample Appointment Title',
            link='https://example.com/appointment.pdf',
            description='Sample Appointment Description'
        )

        payload = {
            'title': 'New Appointment Title',
            'link': 'https://example.com/appointment-new.pdf',
            'description': 'New Appointment Description',
            'time_minutes': 15,
            'price': Decimal('7.80')
        }
        url = detail_url(appointment.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(appointment,k), v)
        self.assertEqual(appointment.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the appointment user results in an error."""
        new_user = create_user(email='user2@example.com', password='testpass123')
        appointment = create_appointment(user=self.user)

        payload = {
            'user': new_user.id
        }
        url = detail_url(appointment.id)
        self.client.patch(url, payload)

        appointment.refresh_from_db()
        self.assertEqual(appointment.user, self.user)

    def test_delete_appointment(self):
        """Test deleting an appointment successful"""
        appointment = create_appointment(user=self.user)

        url = detail_url(appointment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())

    def test_delete_other_users_appointment_error(self):
        """Test trying to delete another users appointments gives error."""
        new_user = create_user(email='user2@example.com', password='testpass123')
        appointment = create_appointment(user=new_user)

        url = detail_url(appointment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Appointment.objects.filter(id=appointment.id).exists())

    def test_create_appointment_with_new_language(self):
        """Test creating an appointment with a new language"""
        payload = {
            'title': 'Sample Interpreting Appointment',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'languages': [{'name': 'Thai'}, {'name': 'Chinese'}]
        }
        res = self.client.post(APPOINTMENT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.filter(user=self.user)
        self.assertEqual(appointment.count(), 1)
        appointment = appointment[0]
        self.assertEqual(appointment.languages.count(), 2)
        for language in payload['languages']:
            exists = appointment.languages.filter(
                name=language['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_appointment_with_existing_languages(self):
        """Test creating an appointment with existing Languages."""
        language_spanish = Language.objects.create(user=self.user, name='Spanish')
        payload = {
            'title': 'Sample Interpreting Appointment',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'languages': [{'name': 'Spanish'}, {'name': 'Chinese'}],
        }
        res = self.client.post(APPOINTMENT_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.filter(user=self.user)
        self.assertEqual(appointment.count(), 1)
        appointment = appointment[0]
        self.assertEqual(appointment.languages.count(), 2)
        self.assertEqual(language_spanish, appointment.languages.all())
        for language in payload['languages']:
            exists = appointment.languages.filter(
                name=language['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


