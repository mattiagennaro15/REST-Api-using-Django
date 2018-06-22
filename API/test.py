import requests
import json

ALLOWED = ["yes","y","no","n"]

def findFlight():

    payload = {
            'dAirport' : "JFK",
    }

    r = requests.get('http://127.0.0.1:8000/searchFlight', data=json.dumps(payload))

findFlight()
