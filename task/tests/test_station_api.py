from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from task.models import Station
from task.serializers import (
    StationListSerializer,
    StationSerializer,
)


STATION_URL = reverse("task:station-list")


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 55.3,
        "longitude": 20.3,
        "service_cost": 2.3,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def detail_url(station_id):
    return reverse("task:station-detail", args=[station_id])


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_station(self):
        sample_station()
        sample_station()
        res = self.client.get(STATION_URL)

        station = Station.objects.all()
        serializer = StationListSerializer(station, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_station_detail(self):
        station = sample_station()

        url = detail_url(station.id)

        res = self.client.get(url)

        serializer = StationSerializer(station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "Sample station",
            "latitude": 55.3,
            "longitude": 20.3,
            "service_cost": 2.3,
        }

        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        payload = {
            "name": "Sample station",
            "latitude": 55.3,
            "longitude": 20.3,
            "service_cost": 2.3,
        }

        res = self.client.post(STATION_URL, payload)
        station = Station.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():

            self.assertEqual(payload[key], getattr(station, key))

    def test_delete_station(self):
        station = sample_station()

        url = detail_url(station.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
