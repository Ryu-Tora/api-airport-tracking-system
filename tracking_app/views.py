from django.db.models import Count, ExpressionWrapper, F, IntegerField
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from tracking_app.models import (
    Airport,
    Route,
    Crew,
    Airplane,
    AirplaneType, Flight, Order, Ticket
)
from tracking_app.permissions import IsAdminOrIfAuthenticatedReadOnly
from tracking_app.serializers import (
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightSerializer,
    OrderSerializer,
    OrderListSerializer,
    RouteListSerializer, FlightListSerializer, FlightDetailSerializer, TicketSerializer,
)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related("source", "destination")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class FlightViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Flight.objects
        .select_related(
            "route__source",
            "route__destination",
            "airplane"
        )
        .prefetch_related("crew")
        .annotate(
            taken_seats=Count("tickets"),
            total_seats=ExpressionWrapper(
                F("airplane__rows") * F("airplane__seats_in_row"),
                output_field=IntegerField(),
            ),
            available_seats=ExpressionWrapper(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets"),
                output_field=IntegerField(),
            )
        )
    )
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("date")

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)
        if destination:
            queryset = queryset.filter(route__destination__name__icontains=destination)
        if date:
            queryset = queryset.filter(departure_time__date=date)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by source name",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by destination name",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="date",
                description="Filter by departure time (YYYY-MM-DD)",
                required=False,
                type=OpenApiTypes.DATE,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route",
        "tickets__flight__airplane",
        "tickets__flight__crew"
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
