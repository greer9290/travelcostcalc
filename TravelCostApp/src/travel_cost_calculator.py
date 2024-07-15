import json, os
from datetime import datetime, timedelta
from pyairports.airports import Airports
import src.google_flights_scraper as gfs
from pathlib import Path
from src import config

airports = Airports()

SLC = airports.airport_iata("SLC")
ATL = airports.airport_iata("ATL")

car_rate_std = 85
meal_cost_std = 80
hotel_cost_std = 165
margin_std = 0.35
numdays_std = 3


def get_rate_multi(destdata):
    if destdata.country != "United States":
        rate_multi = 1.5
        return rate_multi  # 50% increase for international
    
    # Check if west of Salt Lake City or east of Atlanta
    if (destdata.lon > SLC.lon) or (destdata.lon < ATL.lon):
        rate_multi = 1.25
        return rate_multi
    
    rate_multi = 1.00
    return rate_multi  # No increase

def delete_last_flight_data():
    if os.path.exists(config.json_flight_path):
        os.remove(config.json_flight_path)
        print("Deleted last flight json records")
    else:
        print("Delete last flight unsuccessful")
        return

def get_travel_dates(depart_date, return_date, numdays_str):
    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday()))

    if not depart_date and not return_date:
        # No dates provided, use next Monday for a 3-day trip
        dd_dt = next_monday
        rd_dt = dd_dt + timedelta(days=3)
    elif depart_date and not return_date:
        # Only depart date provided, set return date to 3 days after
        dd_dt = datetime.strptime(depart_date, "%Y-%m-%d")
        rd_dt = dd_dt + timedelta(days=3)
    elif depart_date and return_date:
        # Both dates provided, use as is
        dd_dt = datetime.strptime(depart_date, "%Y-%m-%d")
        rd_dt = datetime.strptime(return_date, "%Y-%m-%d")
    else:
        # Only return date provided (invalid case)
        raise ValueError("Return date provided without depart date")

    numdays = int(numdays_str) if numdays_str else (rd_dt - dd_dt).days

    # Format dates for Amadeus API
    depart_date = dd_dt.strftime("%Y-%m-%d")
    return_date = rd_dt.strftime("%Y-%m-%d")

    return depart_date, return_date, numdays


def get_travel_costs(departing_flight, returning_flight, origin, destination, numdays_str, margin_str, avg_hotel_ntly_str, car_rate_str, meal_cost_str):
    # Extract relevant data from the selected flights


    try:
        destdata = airports.airport_iata(destination)
    except Exception as e:
        print(f"Error looking up airport: {str(e)}")
        return None

    rtmult = get_rate_multi(destdata)

    # Use the new function to get formatted dates and numdays
    depart_date, return_date, numdays = get_travel_dates(depart_date, return_date, numdays_str)
    print(depart_date, return_date, numdays)
    try:
        # Flight search
        if flight_cost_str:
            average_flight_price_rt = float(flight_cost_str)
        else:
            departure_price = float(departing_flight[4].replace('$', ''))
            return_price = float(returning_flight[4].replace('$', ''))
            average_flight_price = departure_price + return_price

        # Calculate total and daily costs

        
        car_rate = (float(car_rate_str) if car_rate_str else car_rate_std) * rtmult
        meal_cost_per_day = (float(meal_cost_str) if meal_cost_str else meal_cost_std) * rtmult
        hotel_rate = (int(avg_hotel_ntly_str) if avg_hotel_ntly_str else hotel_cost_std) * rtmult

        margin = float(margin_str) if margin_str else margin_std

        total_hotel_cost = hotel_rate * (numdays - 1)
        total_car_cost = car_rate * numdays
        average_flight_price = average_flight_price_rt
        meal_cost = meal_cost_per_day * numdays

        total_cost = average_flight_price + total_hotel_cost + total_car_cost + meal_cost
        sales_price = total_cost / (1 - margin)

        return depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

