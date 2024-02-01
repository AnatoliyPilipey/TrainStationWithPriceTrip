from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from task.models import Route, Station
from task.serializers import (
    RouteListSerializer,
    RouteDetailSerializer,
)


ROUTE_URL = reverse("task:route-list")


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 55.3,
        "longitude": 20.3,
        "service_cost": 2.3,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def detail_url(route_id):
    return reverse("task:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        station1 = sample_station()
        station2 = sample_station()
        Route.objects.create(
            source=station1,
            destination=station2
        )

        res = self.client.get(ROUTE_URL)

        route = Route.objects.all()
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        station1 = sample_station()
        station2 = sample_station()
        route = Route.objects.create(
            source=station1,
            destination=station2
        )

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        station1 = sample_station()
        station2 = sample_station()
        payload = {
            "source": station1,
            "destination": station2,
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
