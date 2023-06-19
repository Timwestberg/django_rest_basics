"""
Tests for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Language

from appointment.serializers import LanguageSerializer


LANGUAGES_URL = reverse('appointment:language-list')


def detail_url(language_id):
    """Create and return a language detail url"""
    return reverse('appointment:language-detail', args=[language_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class PublicLanguageApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving languages."""
        res = self.client.get(LANGUAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLanguagesApiTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_languages(self):
        """Test retrieving a list of Languages."""
        Language.objects.create(user=self.user, name='Spanish')
        Language.objects.create(user=self.user, name='Tagalog')

        res = self.client.get(LANGUAGES_URL)

        languages = Language.objects.all().order_by('-name')
        serializer = LanguageSerializer(languages, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of languages is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Language.objects.create(user=user2, name='English')
        language = Language.objects.create(user=self.user, name='Yiddish')

        res = self.client.get(LANGUAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], language.name)
        self.assertEqual(res.data[0]['id'], language.id)

    def test_update_language(self):
        """Test updating a language"""
        language = Language.objects.create(user=self.user, name='Spansh')

        payload = {'name': 'Spanish'}
        url = detail_url(language.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        language.refresh_from_db()
        self.assertEqual(language.name, payload['name'])

    def test_delete_language(self):
        """Test deleting a language."""
        language = Language.objects.create(user=self.user, name='British')

        url = detail_url(language.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        languages = Language.objects.filter(user=self.user)
        self.assertFalse(languages.exists())
