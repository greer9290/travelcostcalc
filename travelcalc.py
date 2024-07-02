import tkinter as tk
from tkinter import ttk, messagebox
import csv
import json
from datetime import datetime, timedelta
import os
import time
import pandas as pd
import amadeus
from amadeus import Client, ResponseError
import logging
import ssl
import random
from ttkbootstrap import Style 

import asyncio
import aiohttp

from amadeus import Client, ResponseError
from amadeus.client.decorator import Decorator

from pyairports.airports import Airports
from geopy.distance import geodesic

airports = Airports()

car_rate_std = 85
meal_cost_std = 80
hotel_cost_std = 165
margin_std = 0.35
numdays_std = 3

logger = logging.getLogger('your_logger')
logger.setLevel(logging.DEBUG)

loading_widget = False

# Replace with your Amadeus API credentials
amadeus = Client(
    client_id='OrUx7h1FI2oq4sqL8AWX2nVNJIGglcGw',
    client_secret='1ttndaQhCwXxyDSS',
    hostname='test',
    logger=logger,
)

SLC = airports.airport_iata("SLC")
ATL = airports.airport_iata("ATL")

async def get_rate_multi(destdata, rate_multi):
    if destdata.country != "United States":
        rate_multi = 1.5
        return rate_multi  # 50% increase for international
    
    # Check if west of Salt Lake City or east of Atlanta
    if (destdata.lon < SLC.lon or 
        destdata.lon > ATL.lon):
        rate_multi = 1.25
        return rate_multi
    
    rate_multi = 1.00
    return rate_multi  # No increase


async def get_travel_costs(origin, destination, numdays_str, margin_str, avg_hotel_ntly_str, car_rate_str, meal_cost_str):
    
    try:
        destdata = airports.airport_iata(destination)
    except Exception as e:
        print(f"Error looking up airport: {str(e)}")
        return None

    get_rate_multi(destdata)

    

    car_rate = (float(car_rate_str) if car_rate_str else car_rate_std) * rate_multi
    meal_cost_per_day = (float(meal_cost_str) if meal_cost_str else meal_cost_std) * rate_multi
    hotel_rate = (int(avg_hotel_ntly_str) if avg_hotel_ntly_str else hotel_cost_std) * rate_multi

    margin = float(margin_str) if margin_str else margin_std
    numdays = int(numdays_str) if numdays_str else numdays_std

    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday() + 0))
    depart_date = next_monday.strftime('%Y-%m-%d')
    return_date = (next_monday + timedelta(days=numdays)).strftime('%Y-%m-%d')

    try:
        # Flight search
        flight_response_rt = await asyncio.to_thread(
            amadeus.shopping.flight_offers_search.get,
            originLocationCode=destination,
            destinationLocationCode=origin,
            departureDate=depart_date,
            returnDate=return_date,
            adults=1,
            travelClass='ECONOMY',
            currencyCode='USD'
        )

        flight_prices_rt = [offer['price']['total'] for offer in flight_response_rt.data]
        average_flight_price_rt = sum(float(price) for price in flight_prices_rt) / len(flight_prices_rt) if flight_prices_rt else 0      

        # Calculate total and daily costs

        total_hotel_cost = hotel_rate * numdays
        total_car_cost = car_rate * numdays
        average_flight_price = average_flight_price_rt
        meal_cost = meal_cost_per_day * numdays

        total_cost = average_flight_price + total_hotel_cost + total_car_cost + meal_cost
        sales_price = total_cost / (1 - margin)

        save_api_responses_to_json(origin, destination, flight_response_rt)

        return depart_date, return_date, origin, destination, average_flight_price, total_hotel_cost, total_car_cost, meal_cost, numdays, total_cost, sales_price

    except ResponseError as error:
        print("Amadeus API Error:", error)
        raise Exception("Error fetching data from Amadeus API. See console for details.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

def save_api_responses_to_json(origin, destination, flight_response_rt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"amadeus_responses_{origin}_{destination}_{timestamp}.json"
    
    data = {
        "flight_response_ret": flight_response_rt.data
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Raw API responses saved to {filename}")

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

class TravelCostApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Travel Cost Calculator")
        #self.geometry("1600x800")
        self.state('zoomed') 

        # Apply the flatly theme with a dark mode
        self.style = Style(theme="flatly")
        self.style.theme_use("darkly")  # Switch to dark mode

        self.style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        self.style.configure("Custom.Treeview",
                            background="#2c3e50",
                            foreground="white",
                            fieldbackground="#2c3e50",
                            borderwidth=1,
                            relief="solid")
        
        # Custom styles for buttons
        self.style.configure("Calculate.TButton", foreground="white", background="#4CAF50", font=("Arial", 10, "bold"), borderwidth=0)
        self.style.map("Calculate.TButton", background=[("active", "#45a049")])
        
        self.style.configure("Delete.TButton", foreground="white", background="#FFA500", font=("Arial", 10, "bold"), borderwidth=0)
        self.style.map("Delete.TButton", background=[("active", "#FF8C00")])
        
        self.style.configure("DeleteAll.TButton", foreground="white", background="#FF0000", font=("Arial", 10, "bold"), borderwidth=0)
        self.style.map("DeleteAll.TButton", background=[("active", "#B22222")])



        self.create_widgets()

    def show_loading_window(self):
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Loading")
        self.loading_window.geometry("300x100")
        
        label = ttk.Label(self.loading_window, text="Calculating travel price...")
        label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.loading_window, length=200, mode='indeterminate')
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    def hide_loading_window(self):
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def create_widgets(self):
        # Main Input Frame
        main_input_frame = ttk.Frame(self, padding="15")
        main_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left Input Frame
        left_frame = ttk.Frame(main_input_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right Input Frame
        right_frame = ttk.Frame(main_input_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Configure grid weights for both frames
        for frame in (left_frame, right_frame):
            frame.grid_columnconfigure(1, weight=1)
            for i in range(6):
                frame.grid_rowconfigure(i, weight=1)

        # Left Frame Contents
        ttk.Label(left_frame, text="Origin (airport code):").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=1)
        self.origin_entry = ttk.Entry(left_frame)
        self.origin_entry.grid(row=0, column=1, sticky="ew", pady=1)

        ttk.Label(left_frame, text="Destination (airport code):").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=1)
        self.destination_entry = ttk.Entry(left_frame)
        self.destination_entry.grid(row=1, column=1, sticky="ew", pady=1)

        # Right Frame Contents
        ttk.Label(right_frame, text="Optional Values").grid(row=0, column=0, columnspan=2, sticky="w", pady=1)

        ttk.Label(right_frame, text="Number of Days:").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=1)
        self.days_entry = ttk.Entry(right_frame)
        self.days_entry.grid(row=1, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text="Desired Margin:").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=1)
        self.margin_entry = ttk.Entry(right_frame)
        self.margin_entry.grid(row=2, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text="Hotel rate:").grid(row=3, column=0, sticky="e", padx=(0, 5), pady=1)
        self.hotelrate_entry = ttk.Entry(right_frame)
        self.hotelrate_entry.grid(row=3, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text="Rental Cost (per day):").grid(row=4, column=0, sticky="e", padx=(0, 5), pady=1)
        self.car_rate_entry = ttk.Entry(right_frame)
        self.car_rate_entry.grid(row=4, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Meal Cost (def: ${meal_cost_std})").grid(row=5, column=0, sticky="e", padx=(0, 5), pady=1)
        self.meal_cost_entry = ttk.Entry(right_frame)
        self.meal_cost_entry.grid(row=5, column=1, sticky="ew", pady=1)

        # Buttons Frame
        buttons_frame = ttk.Frame(self, padding="15")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttons_frame, text="Calculate", style="Calculate.TButton", command=self.calculate_and_save).pack(fill=tk.X, padx=5, pady=1)
        ttk.Button(buttons_frame, text="Delete Selected", style="Delete.TButton", command=self.delete_selected).pack(fill=tk.X, padx=5, pady=1)
        ttk.Button(buttons_frame, text="Delete All Items", style="DeleteAll.TButton", command=self.delete_all).pack(fill=tk.X, padx=5, pady=1)

        # Table Frame
        table_frame = ttk.Frame(self, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure Treeview colors and style
        self.style.configure("Treeview", 
                            background="#2c3e50", 
                            foreground="white", 
                            rowheight=25, 
                            fieldbackground="#2c3e50")
        self.style.map("Treeview", background=[("selected", "#34495e")])

        self.style.configure("Treeview.Heading", 
                            background="#34495e", 
                            foreground="white", 
                            relief="flat",
                            font=('Arial', 10, 'bold'))
        self.style.map("Treeview.Heading", 
                    background=[("active", "#2c3e50")])

        # Create the Treeview
        self.tree = ttk.Treeview(table_frame, 
                                columns=('Depart Date', 'Return Date', 'Origin', 'Destination', 
                                        'Flight Price', 'Hotel Cost', 'Car Rental Cost', 'Meal Cost', 
                                        'Number of Days', 'Total Cost', 'Sales Price'), 
                                show='headings',
                                style="Treeview")

        # Configure column headings and widths
        column_widths = {
            'Depart Date': 100,
            'Return Date': 100,
            'Origin': 80,
            'Destination': 80,
            'Flight Price': 100,
            'Hotel Cost': 100,
            'Car Rental Cost': 120,
            'Meal Cost': 100,
            'Number of Days': 120,
            'Total Cost': 100,
            'Sales Price': 100
        }

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=column_widths.get(col, 100), anchor=tk.W)

        # Add a vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Grid layout for Treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        # Configure the grid
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.load_csv_data()
        
    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected row?"):
            item = self.tree.item(selected_item)
            values = item['values']
            
            # Remove from Treeview
            self.tree.delete(selected_item)
            
            # Remove from CSV
            self.delete_from_csv(values)

    def delete_all(self):
            # Ask for confirmation
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all data? This action cannot be undone."):
                # Clear all rows from the Treeview
                for i in self.tree.get_children():
                    self.tree.delete(i)
                
                # Clear all data from the CSV file
                filename = 'travel_costs.csv'
                try:
                    with open(filename, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Depart Date', 'Return Date', 'Origin', 'Destination', 'Flight Price', 'Hotel Cost', 'Car Rental Cost', 'Meal Cost', 'Number of Days', 'Total Cost', 'Sales Price'])  # Write header only
                    print("All data has been deleted from the CSV file.")
                except IOError as e:
                    print(f"Error clearing CSV file: {e}")
                    messagebox.showerror("Error", f"Failed to clear CSV file: {e}")
                    return

                # Optionally, delete all JSON files
                try:
                    for file in os.listdir():
                        if file.startswith("amadeus_responses_") and file.endswith(".json"):
                            os.remove(file)
                    print("All JSON response files have been deleted.")
                except Exception as e:
                    print(f"Error deleting JSON files: {e}")

                messagebox.showinfo("Success", "All data has been deleted successfully.")

    def delete_from_csv(self, values):
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
        
 #       messagebox.showinfo("Success", "Row deleted successfully.")            


    def calculate_and_save(self):
        origin = self.origin_entry.get().upper()
        destination = self.destination_entry.get().upper()
        numdays_str = self.days_entry.get()
        margin_str = self.margin_entry.get()
        avg_hotel_ntly_str = self.hotelrate_entry.get()
        car_rate_str = self.car_rate_entry.get()
        meal_cost_str = self.meal_cost_entry.get()

        try:
            self.show_loading_window()
            
            # Run the asynchronous function
            results = asyncio.run(get_travel_costs(origin, destination, numdays_str, margin_str, avg_hotel_ntly_str, car_rate_str, meal_cost_str))
            
            self.hide_loading_window()
            
            depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price = results
            
            if log_to_csv(depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price):
                messagebox.showinfo("Success", "Data calculated and saved successfully!")
                self.load_csv_data()
            else:
                messagebox.showerror("Error", "Failed to save data to CSV file.")
        except Exception as e:
            self.hide_loading_window()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def load_csv_data(self):
        filename = 'travel_costs.csv'
        if os.path.isfile(filename):
            # Clear existing data
            for i in self.tree.get_children():
                self.tree.delete(i)
            
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print(f"Raw CSV row: {row}")  # Debug print
                    
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

                    # Insert with 'cell' tag to apply borders
                    self.tree.insert('', 'end', values=values)
                    
                    print(f"Processed values: {values}")  # Debug print

            print(f"Treeview columns: {self.tree['columns']}")  # Debug print

if __name__ == "__main__":
    app = TravelCostApp()
    app.mainloop()