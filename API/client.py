import requests
import json
import re

company_list = []
URL = ""
company_type = ""

payment_session = requests.session()

def listCompanies():

    global company_type

    print("\n")
    print("Type 1 to see all the airlines")
    print("Type 2 to see all the payment providers")
    print("Type 3 to see all the companies")
    print("\n")

    company_type = input("Please select what companies you want to see: ")

    if company_type == '1':
        company_type = 'airline'
    elif company_type == '2':
        company_type = 'payment'
    elif company_type == '3':
        company_type = '*'
    else:
        print("Command not found, please try again")
        return

    payload = {"company_type": company_type}

    r = requests.get('http://directory.pythonanywhere.com/api/list/', headers={'Content-Type':'application/json'}, data = json.dumps(payload))

    response = r.json()
    if type(response) is dict:
        companies = response['company_list']
        for company in companies:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Company Name: "+str(company['company_name']))
            print("Company Type: "+str(company['company_type']))
            print("Company URL: "+str(company['url']))
            print("Company code: "+str(company['company_code']))
            print("//////////////////////////////////////////////")
            print("\n")
            company_list.append(company)
    else:
        print("\n")
        print(response)



def findFlight():

    global company_list

    print("Welcome, please type the following:")

    departureDate = str(input("Departure Date (YYYY-MM-DD): "))
    departureAirport = input("Departure Airport: ")
    if departureAirport == "":
        print("You can't leave this space blank")
        return
    destinationAirport = input("Destination Airport: ")
    if destinationAirport == "":
        print("You can't leave this space blank")
        return
    passengerNumber = input("Number of passengers: ")
    if passengerNumber == "":
        print("Please type an integer value")
        return
    isFlexible = input("Are you looking for a flexible ticket (y/n): ")
    if isFlexible == "":
        print("You can't leave this space blank")
        return

    if departureDate and departureAirport and destinationAirport and isFlexible and passengerNumber:
        if departureAirport != destinationAirport:
            if isFlexible.lower() == "yes" or isFlexible.lower() == "y":
                isFlexible = True
            else:
                isFlexible = False
            payload = {'dep_airport': departureAirport.upper(), 'dest_airport': destinationAirport.upper(), 'dep_date': departureDate, 'num_passengers': int(passengerNumber), 'is_flex': isFlexible}
        else:
            print("The departure airport and destination can't have the same name")
    else:
        print("You can't leave some information empty!")


    for company in company_list:
        if company['company_type'] != "payment":
            print("\n")
            print("//////////////////////////////////////////////")
            print(company['company_name'])
            print(company['company_code'])
            print(company['url'])
            print("//////////////////////////////////////////////")
            r = requests.get(company['url']+"/api/findflight/", headers={'Content-Type':'application/json'}, data=json.dumps(payload))

        if r.status_code == 200:
            response = r.json()
            if type(response) is dict:
                for flight in response['flights']:
                    print("\n")
                    print("//////////////////////////////////////////////")
                    print("Flight ID: "+str(flight['flight_id']))
                    print("Flight Number: "+str(flight['flight_num']))
                    print("Departure Airport: "+str(flight['dep_airport']))
                    print("Destination Airport: "+str(flight['dest_airport']))
                    print("Departure time: "+str(flight['dep_datetime']))
                    print("Arrival time: "+str(flight['arr_datetime']))
                    print("Flight duration: "+str(flight['duration']))
                    print("Price: "+str(flight['price']))
                    print("//////////////////////////////////////////////")
        elif r.status_code == 503:
            print("\n")
            print(r.text)
        else:
            print("\n")
            print("ERROR")



def bookFlight():

    global URL
    global company_list

    airlineCode = input("Company code: ")

    for company in company_list:
        if airlineCode == company['company_code']:
            URL = company['url']


    passengers_list = []
    passengers = {}
    flightID = input("Please type the flight ID: ")
    passengerNumber = int(input("Please type the number of passengers: "))

    if passengerNumber <= 0:
        print("Invalid input, retry please")
        return

    for passenger in range(passengerNumber):
        print("Passenger N "+str(int(passenger)+1))

        passengers['first_name'] = input("First name: ")
        if not passengers['first_name']:
            print("Provide a valid input")

        passengers['surname'] = input("Surname: ")
        if not passengers['surname']:
            print("Provide a valid input")

        passengers['email'] = input("E-mail: ")
        if not passengers['email']:
            print("Provide a valid input")

        passengers['phone'] = int(input("Phone number: "))
        if not passengers['phone']:
            print("Provide a valid input")

        passengers_list.append(passengers)

    payload = {'flight_id': flightID, 'passengers': passengers_list}

    r = requests.post(URL+'/api/bookflight/', headers={'Content-Type':'application/json'}, data=json.dumps(payload))

    if r.status_code == 201:
        response = r.json()
        if type(response) is dict:
            booking = response
            print("\n")
            print("//////////////////////////////////////////////")
            print("Booking number: "+str(response['booking_num']))
            print("Booking status: "+str(response['booking_status']))
            print("Total price: "+str(response['tot_price']))
            print("//////////////////////////////////////////////")
    else:
        print("\n")
        print(r.text)


def requestPaymentMethod():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    r = requests.get(URL+'/api/paymentmethods/')

    if r.status_code == 200:
        response = r.json()
        if type(response) is dict:
            payment_service = response['pay_providers']
            for element in payment_service:
                print("\n")
                print("//////////////////////////////////////////////")
                print("ID: "+str(element['pay_provider_id']))
                print("Name: "+str(element['pay_provider_name']))
                print("//////////////////////////////////////////////")

def payForBooking():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    booking_num = input("Please type the booking number: ")
    pay_provider_id = input("Please type the Payment Provider ID: ")

    payload = {'booking_num': booking_num, 'pay_provider_id': pay_provider_id}

    r = requests.post(URL+'/api/payforbooking/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 201:

        response = r.json()

        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Payment provider ID: "+str(response['pay_provider_id']))
            print("Payment provider invoice ID: "+str(response['invoice_id']))
            print("Booking N: "+str(response['booking_num']))
            print("URL: "+str(response['url']))
            print("//////////////////////////////////////////////")

    elif r.status_code == 503:
        print("\n")
        print(r.text)
    else:
        print("\n")
        print("ERROR")

    user_id = input("Type your user ID: ")
    user_psw = input("Type your user pswd: ")

    session = requests.session()


    login = session.post(response['url'] + '/api/login/', data = {'username': user_id, 'password': user_psw })

    payprovider_ref_num = input("Type the invoice ID: ")
    client_ref_num = input("Type the booking number: ")
    amount = input("Type the amount to pay: ")

    payload_client = {'payprovider_ref_num': payprovider_ref_num, 'client_ref_num': client_ref_num, 'amount': amount}

    res = session.post(response['url'] + '/api/payinvoice/', headers = {'Content-Type': 'application/json'}, data = json.dumps(payload_client))

    if res.status_code == 201:
        response = json.loads(res.text)
        print("\n")
        print("//////////////////////////////////////////////")
        print("Unique code: "+str(response['stamp_code']))
        print("//////////////////////////////////////////////")

    elif res.status_code == 503:
        print("\n")
        print(res.text)
    else:
        print("\n")
        print(res.text)


def finaliseBooking():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']


    booking_num = input("Please type the booking number: ")
    pay_provider_id = input("Please type the Payment Provider ID: ")
    stamp = input("Please insert the electronic stamp: ")

    payload = {'booking_num': booking_num, 'pay_provider_id': pay_provider_id, 'stamp': stamp}

    r = requests.post(URL+'/api/finalizebooking/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 201:
        response = r.json()
        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Booking N: "+str(response['booking_num']))
            print("Booking status: "+str(response['booking_status']))
            print("//////////////////////////////////////////////")
    else:
        print("\n")
        print(r.text)


def bookingStatus():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    booking_num = input("Please type the booking number: ")

    payload = {'booking_num': booking_num}

    r = requests.get(URL+'/api/bookingstatus/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 200:
        response = r.json()
        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Booking number: "+str(response['booking_num']))
            print("Booking status: "+str(response['booking_status']))
            print("Flight N: "+str(response['flight_num']))
            print("Departure Airport: "+str(response['dep_airport']))
            print("Destination Airport: "+str(response['dest_airport']))
            print("Departure Date & Time: "+str(response['dep_datetime']))
            print("Arrival Date & Time: "+str(response['arr_datetime']))
            print("Flight duration: "+str(response['duration']))
            print("//////////////////////////////////////////////")
    else:
        print("\n")
        print(r.text)

def cancelBooking():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']


    booking_num = input("Please type the booking number: ")

    payload = {'booking_num': booking_num}

    r = requests.post(URL+'/api/cancelbooking/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 201:
        response = r.json()
        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Booking number: "+str(response['booking_num']))
            print("Booking status: "+str(response['booking_status']))
            print("//////////////////////////////////////////////")
    else:
        print("\n")
        print(r.text)


###############################################################################################################################################################################################


def register():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    first_name = input("Please type your first name: ")
    surname = input("Please type your surname: ")
    email = input("Type your email: ")
    phone = input("Type your phone number: ")
    username = input("Type your username: ")
    password = input("Type your password: ")
    customer_type = input("Costumer type? Personal or business: ")

    payload  = {"first_name": first_name, "surname": surname, "email": email, "phone": phone, "username": username, "password": password, "customer_type": customer_type}

    r = requests.post(URL+'/api/register/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 201:
        print("\n")
        print(r.text)
    elif r.status_code == 503:
        print("\n")
        print(r.text)
    else:
        print(r.text)


def login():

    global URL
    global payment_session

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    username = input("Type your username: ")
    password = input("Type your password: ")

    payment_session = requests.session()

    r = payment_session.post(URL+'/api/login/', data = {"username": username, "password": password})

    if r.status_code == 200:
        print("\n")
        print(r.text)
    elif r.status_code == 503:
        print("\n")
        print(r.text)

def logout():


    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    r = payment_session.post(URL+'/api/logout/')

    if r.status_code == 200:
        print("\n")
        print(r.text)
    elif r.status_code == 503:
        print("\n")
        print(r.text)

def create_new_account():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']


    r = payment_session.post(URL+'/api/newaccount/', headers = {'Content-Type':'application/json'}, data = {} )

    if r.status_code == 201:
        print("\n")
        print(r.text)
    elif r.status_code == 503:
        print("\n")
        print(r.text)


def deposit():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    amount = input("Type the amount you want to add: ")
    account_num = input("Type the account number: ")

    payload = {"amount": amount, "account_num": account_num}

    r = payment_session.post(URL+'/api/deposit/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload) )

    if r.status_code == 201:

        response = r.json()
        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Account number: "+str(response['account_num']))
            print("Balance: "+str(response['balance']))
            print("//////////////////////////////////////////////")

    elif r.status_code == 503:
        print("\n")
        print(r.text)
    elif r.status_code == 500:
        print(r.text)


def transfer():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    amount = input("Type the amount you want to transfer: ")
    from_account_num = input("Type the account number from where the money will be taken: ")
    to_account_num = input("Type the account number to where the money will be paid:  ")

    payload = {"amount": int(amount), "from_account_num": from_account_num, "to_account_num": to_account_num}

    r = payment_session.post(URL+'/api/transfer/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status == 201:
        response = r.json()
        if type(response) is dict:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Account number from where the money have been taken: "+str(response['account_num']))
            print("Balance: "+str(response['balance']))
            print("//////////////////////////////////////////////")

def balance():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']

    r = payment_session.get(URL+'/api/balance/')

    if r.status_code == 200:
        response = r.json()
        for element in response['accounts']:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Account number: "+str(element['account_num']))
            print("Balance: "+str(element['balance']))
            print("//////////////////////////////////////////////")

    elif r.status_code == 503:
        print("\n")
        print(r.text)

def statement():

    global URL

    company_code = input("Please type the company code: ")

    for company in company_list:
        if company_code == company['company_code']:
            URL = company['url']


    account_num = input("Type the account number: ")

    payload = {"account_num": account_num}

    r = payment_session.get(URL+'/api/statement/', headers = {'Content-Type':'application/json'}, data = json.dumps(payload))

    if r.status_code == 201:
        response = r.json()
        for element in response['transactions']:
            print("\n")
            print("//////////////////////////////////////////////")
            print("Transaction date: "+str(element['date']))
            print("Reference number: "+str(element['reference']))
            print("Amount: "+str(element['amount']))
            print("//////////////////////////////////////////////")
    elif r.status_code == 503:
        print("\n")
        print(r.text)
    else:
        print(r.text)


def airline_menu():

    while True:
        print("\nWelcome, this is the list of the commands:\n1)Search Flight\n2)Book flight\n3)Request payment method\n4)Pay for the booking\n5)Finalize the booking\n6)Check the booking status\n7)Cancel the booking\n8)Exit\n")
        choice = input("Please type the number corrispondent to your choice: ")
        if choice == '1':
            findFlight()
        elif choice ==  '2':
            bookFlight()
        elif choice == '3':
            requestPaymentMethod()
        elif choice == '4':
            payForBooking()
        elif choice == '5':
            finaliseBooking()
        elif choice == '6':
            bookingStatus()
        elif choice == '7':
            cancelBooking()
        elif choice == '8':
            return
        else:
            print("Invalid input")
            break

def payment_menu():

    while True:
        print("\nWelcome, this is the list of the commands:\n1)Register\n2)Login\n3)Logout\n4)Create new account\n5)Deposit\n6)Transfer\n7)Check the balance\n8)Statement history\n9)Exit")
        choice = input("Please type the number corrispondent to your choice: ")
        if choice == '1':
            register()
        elif choice ==  '2':
            login()
        elif choice == '3':
            logout()
        elif choice == '4':
            create_new_account()
        elif choice == '5':
            deposit()
        elif choice == '6':
            transfer()
        elif choice == '7':
            balance()
        elif choice == '8':
            statement()
        elif choice == '9':
            return
        else:
            print("Invalid input")
            break

def main():
    listCompanies()
    if company_type == 'airline':
        airline_menu()
    elif company_type == 'payment':
        payment_menu()
    elif company_type == '*':
        choice = input("Would you like to procede with the Airline API or Payment Api? (airline or payment): ")
        if choice == 'airline' or choice == 'AIRLINE':
            airline_menu()
        elif choice == 'payment' or choice == 'PAYMENT':
            payment_menu()
        else:
            print("Input not recognised")
    else:
        print("Input not recognised")

main()
