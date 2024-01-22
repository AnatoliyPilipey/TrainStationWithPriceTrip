from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Count
from task.permissions import IsAdminOrIfAuthenticatedReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from task.models import (
    TrainType,
    Train,
    Journey,
    Crew,
    Route,
    Station,
    Order,
)
from task.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    CrewSerializer,
    CrewListSerializer,
    StationSerializer,
    StationListSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Variety of trains by movement model"""
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    """Name of the train with car number and number of seats in the car"""
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retriv":
            return TrainDetailSerializer
        return TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    """Team member to operate the train"""
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Name of stations where this type of train runs"""
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return StationListSerializer
        return StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source",
        "destination",
    )
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    def list(self, request, *args, **kwargs):
        """Route indicating start and end stations"""
        return super().list(request, *args, **kwargs)


class JourneyPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.prefetch_related(
        "train",
        "route__source",
        "route__destination",
    )
    serializer_class = JourneySerializer
    pagination_class = JourneyPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer

    @staticmethod
    def _params_to_strs(qs):
        """Converts string to a list of string"""
        return [value for value in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("train__cargo_num")
                    * F("train__places_in_cargo")
                    - Count("tickets")
                )
            )
            departure = self.request.query_params.get("departure_date")
            station = self.request.query_params.get("source_station")

            if departure:
                dates = self._params_to_strs(departure)
                queryset = queryset.filter(departure_time__date__in=dates)

            if station:
                queryset = queryset.filter(
                    route__source__name__icontains=station
                )
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_date",
                type={"type": "date"},
                description="Filter by departure date (ex. ?departure_date=2023-10-25,2024-11-12"
            ),
            OpenApiParameter(
                "source_station",
                type={"type": "str"},
                description="Filter by source station name (ex. ?source_station=Ki"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Trip with train, route, crew and cost"""
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 20


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__train__train_type",
        "tickets__journey__route__source",
        "tickets__journey__route__destination",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer

        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """An order created by a registered user with simultaneous purchase of tickets"""
        return super().list(request, *args, **kwargs)
