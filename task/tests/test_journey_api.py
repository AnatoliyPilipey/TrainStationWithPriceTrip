from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db.models import Value, IntegerField
from rest_framework.pagination import PageNumberPagination
from rest_framework.test import APIClient
from rest_framework import status
from task.models import (
    Station,
    Route,
    Journey,
    TrainType,
    Train,
    Crew
)
from task.serializers import (
    JourneyListSerializer,
)


JOURNEY_URL = reverse("task:journey-list")


def sample_crew(**params):
    defaults = {
        "first_name": "Adam",
        "last_name": "Test",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 55.3,
        "longitude": 20.3,
        "service_cost": 2.3,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    station1 = sample_station()
    station2 = sample_station()
    defaults = {
        "source": station1,
        "destination": station2,
    }

    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train(**params):
    train_type = TrainType.objects.create(
        type_name="test_type",
    )
    defaults = {
        "name": "Test train 215",
        "cargo_num": 23,
        "places_in_cargo": 36,
        "kilometer_price": 1.2,
        "train_type": train_type
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class JourneyPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_journey(self):
        Journey.objects.create(
            departure_time="2024-01-12",
            arrival_time="2024-01-15",
            route=sample_route(),
            train=sample_train(),
        )
        res = self.client.get(JOURNEY_URL)
        journey = Journey.objects.all()
        journey = journey.annotate(
            tickets_available=Value(828, output_field=IntegerField())
        )

        serializer = JourneyListSerializer(journey, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
