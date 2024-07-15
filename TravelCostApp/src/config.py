import os
import tempfile

directory = "TravelCostData"
temp_path = tempfile.gettempdir()
path = os.path.join(temp_path, directory)
if os.path.isdir(path):
    data_path = path
else:
    data_path = os.mkdir(path)

csv_filename = "travel_costs.csv"
csv_temp_filename = "temp_travel_costs.csv"
json_filename = "google_flight_results.json"

csv_path = os.path.join(data_path, csv_filename)
csv_temp_path = os.path.join(data_path, csv_temp_filename)
json_flight_path = os.path.join(data_path, json_filename)