# Create your models here.
from django.db import models
from django import forms
from django.utils import timezone
import datetime


# Create your models here.
class Aircraft(models.Model):

    aircraftType = models.CharField(max_length = 10)
    aircraftRegNumb = models.CharField(max_length = 10)
    aircraftSeatNumber = models.PositiveIntegerField()

    def __str__(self):
        return self.aircraftType


class Airport(models.Model):

    airportName = models.CharField(max_length = 100, unique = True)
    airportCountry = models.CharField(max_length = 100)
    airportTimeZone = models.CharField(max_length = 100)

    def __str__(self):
        return self.airportName

class Flight(models.Model):

    flightNumber = models.CharField(max_length = 100, unique = True)
    flightDeparture = models.ForeignKey(Airport, on_delete = models.CASCADE, related_name = "Departure")
    flightDestination = models.ForeignKey(Airport, on_delete = models.CASCADE, related_name = "Arrival")
    flightsDepartureDate = models.DateTimeField()
    flightsArrivalDate = models.DateTimeField()
    flightDuration = models.DurationField()
    aircraftUsed = models.ForeignKey(Aircraft, on_delete = models.CASCADE)
    flightPrice = models.FloatField()

    def __str__(self):
        return "Flight N:"+str(self.flightNumber)+" departing at: "+str(self.flightsDepartureDate)+"\n"


class Person(models.Model):

    firstname = models.CharField(max_length = 100)
    surname = models.CharField(max_length = 100)
    email = models.EmailField()
    phoneNumber = models.PositiveIntegerField()

    def __str__(self):
        return str(self.surname) + " " + str(self.firstname)


class Booking(models.Model):

    enumChoices = (
        ('ON_HOLD', 'ON_HOLD'),
        ('CONFIRMED', 'CONFIRMED'),
        ('CANCELLED', 'CANCELLED'),
        ('TRAVELLED', 'TRAVELLED')
    )

    bookingNumber = models.CharField(max_length = 100, unique = True)
    bookedFlight = models.ForeignKey(Flight, on_delete = models.CASCADE)
    bookingSeats = models.PositiveIntegerField()
    passengerDetails = models.ManyToManyField(Person)
    bookingStatus = models.CharField(max_length = 10, choices = enumChoices, default = 'ON_HOLD')
    bookingDuration = models.DateField()

    def __str__(self):
        return self.bookingNumber

class PaymentProvider(models.Model):

    paymentProviderName = models.CharField(max_length = 100)
    paymentAddress = models.URLField()
    accountNumber = models.PositiveIntegerField(unique = True)
    accountUsername = models.CharField(max_length = 50, unique = True)
    accountPassword = models.CharField(max_length = 50, default = "")

    def __str__(self):
        return self.paymentProviderName

class Invoice(models.Model):

    paymentReferenceNumber = models.PositiveIntegerField(unique = True)
    bookingN = models.ForeignKey(Booking, on_delete = models.CASCADE)
    amount = models.CharField(max_length = 50, default = "0")
    invoicePayed = models.BooleanField()
    alphanumericCode = models.CharField(max_length = 20, unique = True)

    def __str__(self):
        return str(self.paymentReferenceNumber)
