# Generated by Django 2.0.3 on 2018-03-19 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aircraftType', models.CharField(max_length=4)),
                ('aircraftRegNumb', models.CharField(max_length=10)),
                ('aircraftSeatNumber', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airportName', models.CharField(max_length=100, unique=True)),
                ('airportCountry', models.CharField(max_length=100)),
                ('airportTimeZone', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookingNumber', models.CharField(max_length=100, unique=True)),
                ('bookingSeats', models.PositiveIntegerField()),
                ('bookingStatus', models.CharField(choices=[('ON_HOLD', 'ON_HOLD'), ('CONFIRMED', 'CONFIRMED'), ('CANCELLED', 'CANCELLED'), ('TRAVELLED', 'TRAVELLED')], default='ON_HOLD', max_length=10)),
                ('bookingDuration', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flightNumber', models.CharField(max_length=100, unique=True)),
                ('flightsDepartureDate', models.DateTimeField()),
                ('flightsArrivalDate', models.DateTimeField()),
                ('flightDuration', models.DurationField()),
                ('flightPrice', models.FloatField()),
                ('aircraftUsed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.Aircraft')),
                ('flightDeparture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Departure', to='airlines.Airport')),
                ('flightDestination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Arrival', to='airlines.Airport')),
            ],
        ),
        migrations.CreateModel(
            name='Invoices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentReferenceNumber', models.PositiveIntegerField(unique=True)),
                ('amount', models.CharField(default='0', max_length=50)),
                ('invoicePayed', models.BooleanField()),
                ('alphanumericCode', models.CharField(max_length=20, unique=True)),
                ('bookingN', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.Booking')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProviders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentProviderName', models.CharField(max_length=100)),
                ('paymentAddress', models.URLField()),
                ('accountNumber', models.PositiveIntegerField(unique=True)),
                ('accountUsername', models.CharField(max_length=50, unique=True)),
                ('accountPassword', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phoneNumber', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='bookedFlight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.Flight'),
        ),
        migrations.AddField(
            model_name='booking',
            name='passengerDetails',
            field=models.ManyToManyField(to='airlines.Person'),
        ),
    ]
