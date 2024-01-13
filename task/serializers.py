from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from task.models import (
    TrainType,
    Train,
    Journey,
    Crew,
    Route,
    Station,
    Ticket,
    Order,
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "type_name",)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "kilometer_price",
            "train_type",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.StringRelatedField()

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "capacity",
            "train_type",
        )


class TrainDetailSerializer(TrainSerializer):
    train_type = serializers.StringRelatedField()

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "capacity",
            "train_type",
            "kilometer_price",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(CrewSerializer):

    class Meta:
        model = Crew
        fields = ("id", "full_name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude",
            "service_cost",
        )


class StationListSerializer(StationSerializer):
    class Meta:
        model = Station
        fields = (
            "id",
            "name",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class RouteListSerializer(RouteSerializer):
    direction = serializers.CharField(
        source="__str__",
        read_only=True,
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "direction"
        )


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "train",
            "crew",
        )


class JourneyListSerializer(JourneySerializer):
    route = serializers.StringRelatedField()
    train = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_time",
            "route",
            "train",
            "price_trip",
            "tickets_available",
        )


class JourneyDetailSerializer(JourneySerializer):
    route = serializers.StringRelatedField()
    crew = CrewSerializer(
        many=True,
        read_only=True,
    )
    train = serializers.StringRelatedField()
    distance = serializers.FloatField(
        source="route.distance",
        read_only=True
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "train",
            "crew",
            "distance",
            "price_trip",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo_num"],
            attrs["place_in_cargo"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = (
            "id",
            "journey",
            "cargo_num",
            "place_in_cargo"
        )


class TicketDetailSerializer(TicketSerializer):
    departure_time = serializers.DateTimeField(
        source="journey.departure_time",
        read_only=True
    )
    arrival_time = serializers.DateTimeField(
        source="journey.arrival_time",
        read_only=True
    )
    source = serializers.CharField(
        source="journey.route.source.name",
        read_only=True,
    )
    destination = serializers.CharField(
        source="journey.route.destination.name",
        read_only=True,
    )
    train = serializers.CharField(
        source="journey.train.name",
        read_only=True,
    )
    price_trip = serializers.FloatField(
        source="journey.price_trip",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "source",
            "destination",
            "train",
            "cargo_num",
            "place_in_cargo",
            "price_trip",
        )


class TicketListSerializer(TicketDetailSerializer):
    route = serializers.StringRelatedField(
        source="journey.route",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "departure_time",
            "route",
            "price_trip",
        )


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets"
        )


class OrderCreateSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
        )


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )
