from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)

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
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"Train:{self.name} all places:{self.capacity}"
