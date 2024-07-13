import csv
import os
import time

def load_csv_data(tree):
    filename = 'travel_costs.csv'
    if os.path.isfile(filename):
        # Clear existing data
        for i in tree.get_children():
            tree.delete(i)
        
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:                    
                # Explicitly map CSV columns to Treeview columns
                values = [
                    row.get('Depart Date', 'N/A'),
                    row.get('Return Date', 'N/A'),
                    row.get('Origin', 'N/A'),
                    row.get('Destination', 'N/A'),
                    row.get('Flight Price', 'N/A'),
                    row.get('Hotel Cost', 'N/A'),
                    row.get('Car Rental Cost', 'N/A'),
                    row.get('Meal Cost', 'N/A'),
                    row.get('Number of Days', 'N/A'),
                    row.get('Total Cost', 'N/A'),
                    row.get('Sales Price', 'N/A')
                ]
                tree.insert('', 'end', values=values)


def log_to_csv(depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price):
    filename = 'travel_costs.csv'
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        try:
            file_exists = os.path.isfile(filename)
            
            with open(filename, 'a', newline='') as csvfile:
                fieldnames = ['Depart Date', 'Return Date', 'Origin', 'Destination', 'Flight Price', 'Hotel Cost', 'Car Rental Cost', 'Meal Cost', 'Number of Days', 'Total Cost', 'Sales Price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                writer.writerow({
                    'Depart Date': depart_date,
                    'Return Date': return_date,
                    'Origin': origin,
                    'Destination': destination,
                    'Flight Price': f"${average_flight_price:.2f}",
                    'Hotel Cost': f"${hotel_cost:.2f}",
                    'Car Rental Cost': f"${car_cost:.2f}",
                    'Meal Cost': f"${meal_cost:.2f}",
                    'Number of Days': f"{numdays}",
                    'Total Cost': f"${total_cost:.2f}",
                    'Sales Price': f"${sales_price:.2f}"
                })
            
            return True
        
        except (PermissionError, IOError) as e:
            print(f"Error writing to file: {e}. Attempt {attempt + 1} of {max_attempts}")
            attempt += 1
            time.sleep(2)

        return False
    
def delete_from_csv(values):
        filename = 'travel_costs.csv'
        temp_filename = 'temp_travel_costs.csv'
        
        with open(filename, 'r') as csvfile, open(temp_filename, 'w', newline='') as tempfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(tempfile)
            
            headers = next(reader)
            writer.writerow(headers)
            
            for row in reader:
                if row != values:
                    writer.writerow(row)
        
        os.remove(filename)
        os.rename(temp_filename, filename)
