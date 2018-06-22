from django.contrib import admin
from .models import Aircraft, Airport, Flight, Person, Booking, PaymentProvider, Invoice

# Register your models here.

admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Person)
admin.site.register(Booking)
admin.site.register(PaymentProvider)
admin.site.register(Invoice)
