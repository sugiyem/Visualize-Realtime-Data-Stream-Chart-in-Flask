import requests 
import time
import random
import math
from datetime import datetime

# URL to which the POST request will be sent
url = 'http://127.0.0.1/data'

# Headers for the POST request
headers = {
    'Content-Type': 'application/json'
}

count = 0
while True:
    try:
        x = math.sin(math.pi * count / 20) + random.normalvariate(0., 1e-2)
        y = x ** 2 + random.normalvariate(0., 1e-2)
        count += 1
        data = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'x': x,
            'y': y,
            'lon': round(random.uniform(-180.0, 180.0), 3),
            'lat': round(random.uniform(-90.0, 90.0), 3),
            'heigh': round(random.random(), 3),
            'rtk': round(random.random(), 3),
            'hrms': round(random.random(), 3),
            'vhrms': round(random.random(), 3)
        }

        # Sending the POST request
        response = requests.post(url, json=data, headers=headers)
        
        # Wait for a short interval before sending the next request
        time.sleep(1)  # Adjust the sleep time as needed
        
    except requests.exceptions.RequestException as e:
        # Handling any exceptions that occur during the request
        print(f"An error occurred: {e}")
        # Optionally, you can break the loop or handle the error in a specific way
        time.sleep(5)  # Wait for a longer interval before retrying
