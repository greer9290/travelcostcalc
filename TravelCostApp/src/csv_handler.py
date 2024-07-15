import csv
import os
import time
from pathlib import Path
from src import config
# Construct the absolute path to the csv file

def log_to_csv(depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price):
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        try:
            file_exists = os.path.isfile(config.csv_path)
            
            with open(config.csv_path, 'a', newline='') as csvfile:
                fieldnames = ['Depart Date', 'Return Date', 'Origin', 'Destination', 'Flight Price', 'Hotel Cost', 'Car Rental Cost', 'Meal Cost', 'Number of Days', 'Total Cost', 'Sales Price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                new_row = {
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
                }
                writer.writerow(new_row)
                print(f"New row written to CSV: {new_row}")
                
                # Add this check
                with open(config.csv_path, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    row_count = sum(1 for row in reader) - 1  # Subtract 1 for header
                    print(f"CSV file now contains {row_count} data rows")

                return True

        except (PermissionError, IOError) as e:
            print(f"Error writing to file: {e}. Attempt {attempt + 1} of {max_attempts}")
            attempt += 1
            time.sleep(2)

            print("Failed to write to CSV after multiple attempts")
            return False


def load_csv_data(tree):
    if os.path.isfile(config.csv_path):
        print(f"CSV data exists at path: {config.csv_path}")
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            with open(config.csv_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # Read the first row as headers
                
                # Map the headers to the correct column names
                column_map = {
                    'Depart Date': 0,
                    'Return Date': 1,
                    'Origin': 2,
                    'Destination': 3,
                    'Flight Price': 4,
                    'Hotel Cost': 5,
                    'Car Rental Cost': 6,
                    'Meal Cost': 7,
                    'Number of Days': 8,
                    'Total Cost': 9,
                    'Sales Price': 10
                }
                
                row_count = 0
                for row in reader:
                    row_count += 1
                    print(f"Processing row {row_count}:", row)
                    values = [row[column_map[col]] for col in column_map]
                    tree.insert('', 'end', values=values)
                print(f"Total rows processed: {row_count}")
            print("CSV data loaded successfully")
        except FileNotFoundError:
            print(f"CSV file not found at: {config.csv_path}")
        except csv.Error as e:
            print(f"Error reading CSV file: {e}")
        except Exception as e:
            print(f"Unexpected error loading CSV data: {e}")
    else:
        print(f"CSV file not found at: {config.csv_path}")

    # Check if any items were added to the tree
    if len(tree.get_children()) == 0:
        print("No items in treeview after loading CSV data")
    else:
        print(f"Treeview loaded with {len(tree.get_children())} items")
    
def delete_from_csv(values):
        
        with open(config.csv_path, '+w') as csvfile, open(csv_temp_path, '+', newline='') as tempfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(tempfile)
            
            headers = next(reader)
            writer.writerow(headers)
            
            for row in reader:
                if row != values:
                    writer.writerow(row)
        
        os.remove(config.csv_path)
        os.rename(msw.csv_temp_path, config.csv_path)
