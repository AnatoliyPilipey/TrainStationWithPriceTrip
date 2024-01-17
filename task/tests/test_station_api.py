
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


STATION_URL = reverse("task:station-list")


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
