import requests
import json
import csv
from datetime import datetime, timedelta
from statistics import mean

def get_travel_costs(origin, destination):
    # Calculate dates
    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday() + 0) % 7)
    depart_date = next_monday.strftime('%Y-%m-%d')
    return_date = (next_monday + timedelta(days=2)).strftime('%Y-%m-%d')

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"

    querystring = {
        "fromId": f"{origin}.AIRPORT",
        "toId": f"{destination}.AIRPORT",
        "departDate": depart_date,
        "returnDate": return_date,
        "pageNo": "1",
        "adults": "1",
        "sort": "BEST",
        "cabinClass": "ECONOMY",
        "currency_code": "USD"
    }

    headers = {
        "x-rapidapi-key": "4d87f2e38bmsh9edec9158c5a627p124f79jsn1f71396e4dcf",
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    flight_data = response.json()
    print(json.dumps(flight_data, indent=2))

    # Extract prices and calculate average
    prices = []
    for offer in flight_data['data']['flightOffers']:
        total_price = offer['priceBreakdown']['total']
        price = total_price['units'] + total_price['nanos'] / 1e9
        prices.append(price)

    if prices:
        average_price = mean(prices)
    else:
        average_price = 0  # or handle this case as appropriate for your application

    # Hotel and car rental costs (placeholders)
    hotel_cost = 100
    car_cost = 50

    return average_price, hotel_cost, car_cost, average_price + hotel_cost + car_cost

def log_to_csv(origin, destination, average_price):
    filename = 'travel_costs.csv'
    file_exists = False
    try:
        with open(filename, 'r') as csvfile:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Date', 'Origin', 'Destination', 'Average Price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Origin': origin,
            'Destination': destination,
            'Average Price': f"${average_price:.2f}"
        })

def main():
    origin = input("Enter the origin airport code (e.g., DFW): ").upper()
    destination = input("Enter the destination airport code (e.g., MCI): ").upper()

    try:
        average_price, hotel_cost, car_cost, total_cost = get_travel_costs(origin, destination)

        response = {
            "origin": origin,
            "destination": destination,
            "average_flight_price": f"${average_price:.2f}",
            "hotel_cost": f"${hotel_cost:.2f}",
            "car_rental_cost": f"${car_cost:.2f}",
            "total_cost": f"${total_cost:.2f}"
        }

        print(json.dumps(response, indent=2))

        log_to_csv(origin, destination, average_price)
        print("\nAverage flight price has been appended to travel_costs.csv")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your input and try again.")

if __name__ == "__main__":
    main()