
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Flight, Airport, Booking, Person, PaymentProvider, Invoice
import datetime
from datetime import timedelta, timezone
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import random
import string
from django.core.exceptions import ObjectDoesNotExist
import requests
import pytz
from pytz import timezone

# Create your views here.
def findFlight(request, format=None):

    flight_dictionary = {}
    flight_list = []

    if request.method == "GET":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        departureAirport = body['dep_airport']
        destinationAirport = body['dest_airport']
        departureDate = body['dep_date']
        passengerNumber = body['num_passengers']
        flexible = body['is_flex']

        try:
            ddate = datetime.datetime.strptime(departureDate, "%Y-%m-%d")
        except ObjectDoesNotExist:
            return HttpResponse("Format of the date incorrect", status = 503)

        if not flexible:
            try:
                flights = Flight.objects.all().filter(flightsDepartureDate__year = ddate.year, flightsDepartureDate__month = ddate.month, flightsDepartureDate__day = ddate.day, flightDeparture__airportName = departureAirport, flightDestination__airportName = destinationAirport)
            except ObjectDoesNotExist:
                return HttpResponse("Could not create the flight object", status = 503)
        else:
            try:
                flights = Flight.objects.all().filter(flightsDepartureDate__range = [ddate - timedelta(days=3), ddate + timedelta(days=3)], flightDeparture__airportName = departureAirport, flightDestination__airportName = destinationAirport)
            except ObjectDoesNotExist:
                return HttpResponse("Could not create the flight object", status = 503)

        if flights:
            departure = Airport.objects.get(airportName = departureAirport)
            destination = Airport.objects.get(airportName = destinationAirport)
            destinationtz = timezone(destination.airportTimeZone)
            departuretz = timezone(departure.airportTimeZone)

            for flight in flights:
                departure_timezone = flight.flightsDepartureDate.astimezone(departuretz)
                duration_converted =  departure_timezone + flight.flightDuration
                destination_converted = duration_converted.astimezone(destinationtz)
                empty_flight_dictionaty = {}
                empty_flight_dictionaty['flight_id'] = str(flight.id)
                empty_flight_dictionaty['flight_num'] = flight.flightNumber
                empty_flight_dictionaty['dep_airport'] = str(departure)
                empty_flight_dictionaty['dest_airport'] = str(destination)
                empty_flight_dictionaty['dep_datetime'] = str(departure_timezone.strftime("%Y-%m-%d %H:%M"))
                empty_flight_dictionaty['arr_datetime'] = str(destination_converted.strftime("%Y-%m-%d %H:%M"))
                empty_flight_dictionaty['duration'] = str(flight.flightDuration)
                empty_flight_dictionaty['price'] = str(flight.flightPrice)
                flight_list.append(empty_flight_dictionaty)
            flight_dictionary['flights'] = flight_list

            return HttpResponse(json.dumps(flight_dictionary), status = 200)
        else:
            return HttpResponse("No flights found", status = 503)

@csrf_exempt
def bookFlight(request, format = None):

    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        flightID = body['flight_id']
        passengers = body['passengers']

        seats = len(passengers)

        try:
            flight = Flight.objects.get(pk = flightID)
        except ObjectDoesNotExist:
            return HttpResponse("No flights found with this id!", status = 503)

        total_seats = flight.aircraftUsed.aircraftSeatNumber
        seat_taken = 0

        try:
            booking_with_same_id = Booking.objects.filter(bookedFlight = flight)
        except ObjectDoesNotExist:
            return HttpResponse("Could not create the Booking object", status = 503)

        for book in booking_with_same_id:
            seat_taken += book.bookingSeats
            if total_seats < (seat_taken + book.bookingSeats):
                return HttpResponse("No more seats available, only " +str(total_seats - seat_taken)+ " remained", status = 503)

        booking_num = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        booking_status = "ON_HOLD"

        booking = Booking(
                        bookingNumber = booking_num,
                        bookingStatus = booking_status,
                        bookedFlight = flight,
                        bookingSeats = int(seats),
                        bookingDuration = datetime.datetime.now() + timedelta(days=7),
                        )
        booking.save()

        for p in passengers:
            person = Person(
                            firstname = p['first_name'],
                            surname = p['surname'],
                            email = p['email'],
                            phoneNumber = p['phone']
                            )
            person.save()
            booking.passengerDetails.add(person)

        price = flight.flightPrice

        total_price = seats * price

        payload = {'booking_num': booking.bookingNumber, 'booking_status': booking.bookingStatus, 'tot_price': total_price }

        return HttpResponse(json.dumps(payload), status = 201)

def requestPaymentMethod(request):

    if request.method == "GET":

        pay_providers = []
        payload = {}

        payments_provider = PaymentProvider.objects.all()


        if payments_provider.count() == 0:
            return JsonResponse("No payment providers available", status = 503, safe = False)

        for p in payments_provider:
            empty_dict = {}
            empty_dict['pay_provider_id'] = p.id
            empty_dict['pay_provider_name'] = p.paymentProviderName
            pay_providers.append(empty_dict)

        payload['pay_providers'] = pay_providers

        return HttpResponse(json.dumps(payload), status = 200)


@csrf_exempt
def payForBooking(request):

    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        pay_provider_id = body['pay_provider_id']
        booking_num = body['booking_num']

        paymentProvider = PaymentProvider.objects.get(pk = pay_provider_id)
        booking = Booking.objects.get(bookingNumber = booking_num)

        if not booking or not paymentProvider:
            return HttpResponse("Booking number or payment provider ID invalid!", status = 503)

        if datetime.datetime.now() == booking.bookingDuration:
            return HttpResponse("This booking has expired!", status = 503)

        payload = {'account_num': str(paymentProvider.accountNumber), 'client_ref_num': str(booking.bookingNumber), 'amount': str(booking.bookingSeats * booking.bookedFlight.flightPrice)}

        session = requests.session()

        login = session.post(paymentProvider.paymentAddress + 'api/login/', data = {'username': paymentProvider.accountUsername, 'password': paymentProvider.accountPassword })
        res = session.post(paymentProvider.paymentAddress + 'api/createinvoice/', headers = {'Content-Type': 'application/json'}, data = json.dumps(payload))

        if res.status_code == 201:

            response = json.loads(res.text)

            invoice = Invoice( paymentReferenceNumber = response['payprovider_ref_num'],
                                bookingN = booking,
                                amount = str(booking.bookingSeats * booking.bookedFlight.flightPrice),
                                invoicePayed = False,
                                alphanumericCode = response['stamp_code'])
            invoice.save()

            if invoice:

                payload_client = {  'pay_provider_id': paymentProvider.id,
                                    'invoice_id': invoice.paymentReferenceNumber,
                                    'booking_num': booking.bookingNumber,
                                    'url': paymentProvider.paymentAddress
                                }

                return HttpResponse(json.dumps(payload_client), status = 201)

            else:

                return HttpResponse("Could not create the invoice", status = 503)

        else:
            return HttpResponse(res, status = 503)


@csrf_exempt
def finalizeBooking(request):

    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        booking_num = body['booking_num']
        pay_provider_id = body['pay_provider_id']
        stamp = body['stamp']

        try:
            booking = Booking.objects.get(bookingNumber = booking_num)
        except:
            return HttpResponse("Could not create the booking object", status = 503)

        try:
            invoice = Invoice.objects.get(bookingN = booking)
        except:
            return HttpResponse("Invoice could not be created", status = 503)

        if stamp == invoice.alphanumericCode:
            booking.bookingStatus = "CONFIRMED"
            booking.save()

            invoice.invoicePayed = True
            invoice.save()

            payload = { 'booking_num': invoice.bookingN.bookingNumber,
                        'booking_status': booking.bookingStatus }

            return HttpResponse(json.dumps(payload), status = 201)
        else:
            return HttpResponse("The electronic stamp does not exist", status = 503)


def bookingStatus(request):

    if request.method == "GET":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        booking_num = body['booking_num']

        try:
            bookings = Booking.objects.all().filter(bookingStatus = "CONFIRMED")
        except:
            return HttpResponse("Could not create the Booking objects", status = 503)

        try:
            booking = Booking.objects.get(bookingNumber = booking_num)
        except:
            return HttpResponse("Could not create the Booking object", status = 503)


        booking_num = booking.bookingNumber
        booking_status = booking.bookingStatus
        flight_num = booking.bookedFlight.flightNumber
        dep_airport = booking.bookedFlight.flightDeparture.airportName
        dest_airport = booking.bookedFlight.flightDestination.airportName

        destinationtz = timezone(booking.bookedFlight.flightDestination.airportTimeZone)
        departuretz = timezone(booking.bookedFlight.flightDeparture.airportTimeZone)
        departure_timezone = booking.bookedFlight.flightsDepartureDate.astimezone(departuretz)
        duration_converted =  departure_timezone + booking.bookedFlight.flightDuration
        destination_converted = duration_converted.astimezone(destinationtz)

        dep_datetime = departure_timezone
        arr_datetime = destination_converted
        duration = booking.bookedFlight.flightDuration


        payload = { 'booking_num': booking_num,
                    'booking_status': booking_status,
                    'flight_num': flight_num,
                    'dep_airport': dep_airport,
                    'dest_airport': dest_airport,
                    'dep_datetime': str(dep_datetime.strftime("%Y-%m-%d %H:%M")),
                    'arr_datetime': str(arr_datetime.strftime("%Y-%m-%d %H:%M")),
                    'duration': str(duration)}

        return HttpResponse(json.dumps(payload), status = 200)

@csrf_exempt
def cancelBooking(request):

    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        booking_num = body['booking_num']

        booking = Booking.objects.get(bookingNumber = booking_num)

        if booking:
            booking.bookingStatus = "CANCELLED"
            booking.save()
            payload = {'booking_num': booking.bookingNumber, 'booking_status': booking.bookingStatus}

            return HttpResponse(json.dumps(payload), status = 201)

        else:
            return HttpResponse("This booking number does not exist", status = 503)
