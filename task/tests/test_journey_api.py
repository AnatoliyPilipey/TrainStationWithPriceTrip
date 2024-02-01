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
    JourneyDetailSerializer,
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
    try:
        return Train.objects.get(pk=1)
    except Exception:
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


def detail_url(journey_id):
    return reverse("task:journey-detail", args=[journey_id])


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

    def test_retrieve_journey_detail(self):
        journey = Journey.objects.create(
            departure_time="2024-01-12T00:00:00",
            arrival_time="2024-01-13T00:00:00",
            route=sample_route(),
            train=sample_train(),
        )

        url = detail_url(journey.id)
        res = self.client.get(url)

        serializer = JourneyDetailSerializer(journey)
        print()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_journey_by_date(self):
        Journey.objects.create(
            departure_time="2023-01-12T00:00:00",
            arrival_time="2023-01-13T00:00:00",
            route=sample_route(),
            train=sample_train(),
        )

        Journey.objects.create(
            departure_time="2024-01-12T00:00:00",
            arrival_time="2024-01-13T00:00:00",
            route=sample_route(),
            train=sample_train(),
        )

        Journey.objects.create(
            departure_time="2025-01-12T00:00:00",
            arrival_time="2025-01-13T00:00:00",
            route=sample_route(),
            train=sample_train(),
        )

        journey = Journey.objects.all().annotate(
            tickets_available=Value(828, output_field=IntegerField())
        )

        journey1 = journey.get(pk=1)
        serializer1 = JourneyListSerializer(journey1, many=False)

        journey2 = journey.get(pk=2)
        serializer2 = JourneyListSerializer(journey2, many=False)

        journey3 = journey.get(pk=3)
        serializer3 = JourneyListSerializer(journey3, many=False)

        res = self.client.get(
            JOURNEY_URL,
            {"departure_date": "2023-01-12,2024-01-12"}
        )

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_journey_by_source_station(self):
        station1 = sample_station(
            name="Kiev",
        )

        Journey.objects.create(
            departure_time="2023-01-12T00:00:00",
            arrival_time="2023-01-13T00:00:00",
            route=sample_route(
                source=station1
            ),
            train=sample_train(),
        )

        station2 = sample_station(
            name="Parish",
        )

        Journey.objects.create(
            departure_time="2023-01-12T00:00:00",
            arrival_time="2023-01-13T00:00:00",
            route=sample_route(
                source=station2
            ),
            train=sample_train(),
        )

        journey = Journey.objects.all().annotate(
            tickets_available=Value(828, output_field=IntegerField())
        )

        journey1 = journey.get(pk=1)
        serializer1 = JourneyListSerializer(journey1, many=False)

        journey2 = journey.get(pk=2)
        serializer2 = JourneyListSerializer(journey2, many=False)

        res = self.client.get(
            JOURNEY_URL,
            {"source_station": "Kie"}
        )

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])
