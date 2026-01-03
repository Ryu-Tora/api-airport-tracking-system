from django.urls import path, include
from rest_framework import routers

from tracking_app.views import (
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    FlightViewSet,
    OrderViewSet
)

app_name = "tracking_app"

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("routs", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
