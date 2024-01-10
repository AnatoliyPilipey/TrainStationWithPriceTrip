from django.urls import path, include
from rest_framework import routers
from task.views import (
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    JourneyViewSet,
)

router = routers.DefaultRouter()
router.register("train_type", TrainTypeViewSet)
router.register("train", TrainViewSet)
router.register("crew", CrewViewSet)
router.register("station", StationViewSet)
router.register("route", RouteViewSet)
router.register("journey", JourneyViewSet)


urlpatterns = [path("", include(router.urls))]


app_name = "task"
