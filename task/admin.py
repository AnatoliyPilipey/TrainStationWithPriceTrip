from django.contrib import admin

from .models import (
    Crew,
    TrainType,
    Train,
    Order,
    Ticket,
    Station,
    Route,
    Journey
)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)


admin.site.register(Crew)
admin.site.register(TrainType)
admin.site.register(Ticket)
admin.site.register(Train)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Journey)
