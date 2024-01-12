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


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
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
