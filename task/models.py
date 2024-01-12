from django.db import models
from math import radians, sin, cos, sqrt, atan2
from django.core.exceptions import ValidationError
from django.conf import settings


def station_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
) -> float:
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    earth_radius = 6371.0
    distance = earth_radius * c

    return distance


class Crew(models.Model):
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class TrainType(models.Model):
    type_name = models.CharField(max_length=65, unique=True)

    def __str__(self):
        return self.type_name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    kilometer_price = models.FloatField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"Train:{self.name} all places:{self.capacity}"


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    service_cost = models.FloatField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routers_source"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routers_destination"
    )

    def __str__(self):
        return f"Source:{self.source.name} destination:{self.destination.name}"

    @property
    def distance(self) -> float:
        return station_distance(
            self.source.latitude,
            self.source.longitude,
            self.destination.latitude,
            self.destination.longitude
        )


class Journey(models.Model):
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="journey")

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return f"Departure time:{self.departure_time} arrival time:{self.arrival_time}"

    @property
    def price_trip(self) -> float:
        price_distance = self.route.distance * self.train.kilometer_price
        return (
            price_distance
            + self.route.source.service_cost
            + self.route.destination.service_cost
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    cargo_num = models.IntegerField()
    place_in_cargo = models.IntegerField()

    @staticmethod
    def validate_ticket(cargo_num, place_in_cargo, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo_num, "cargo_num", "cargo_num"),
            (place_in_cargo, "place_in_cargo", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo_num,
            self.place_in_cargo,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{str(self.journey)} (row: {self.cargo_num}, seat: {self.place_in_cargo})"
        )

    class Meta:
        unique_together = ("journey", "cargo_num", "place_in_cargo")
        ordering = ["cargo_num", "place_in_cargo"]
