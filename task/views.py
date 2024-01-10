from rest_framework import viewsets
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
from task.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
