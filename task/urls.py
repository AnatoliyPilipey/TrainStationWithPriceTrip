from django.urls import path, include
from rest_framework import routers
from task.views import (
    TrainTypeViewSet,
)

router = routers.DefaultRouter()
router.register("train_type", TrainTypeViewSet)


urlpatterns = [path("", include(router.urls))]


app_name = "task"
