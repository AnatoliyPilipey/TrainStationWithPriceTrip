from rest_framework import serializers
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

