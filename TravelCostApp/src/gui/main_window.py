# src/gui/main_window.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os, csv, json
from src.gui import simple_calendar
from src.gui.settings_tab import SettingsTab as settab
from src.gui.flight_data_tab import FlightDataTab as fdt 
import src.travel_cost_calculator as tcc
import src.csv_handler as csvh
from src import config
from src import google_flights_scraper as gfs
from src import travel_cost_calculator as tcc
import threading
import queue



class TravelCostApp(ttk.Window):
    def __init__(self):
        self.settings = self.load_settings()
        self.current_theme = self.settings.get('theme', 'cosmo')
        super().__init__(themename=self.current_theme)
        
        self.selection_event = threading.Event()
        self.selection_queue = queue.Queue()
        
        self.sort_order = []
        
        self.title("Travel Cost Calculator")
        self.state('zoomed')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Travel Cost Calculator")

        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        self.settings_frame = settab(self.notebook, self)
        self.notebook.add(self.settings_frame, text="Settings")
        

        
        self.flight_data_title = tk.StringVar(value="Departure Flights")
        self.selected_departure = None
        self.selected_return = None

        self.create_widgets()
        self.create_results_tab()
        self.create_flight_data_treeview()

        # Load CSV data after widgets are created
        csvh.load_csv_data(self.tree)
        
    def create_flight_data_treeview(self):
        self.flight_data_frame = ttk.Frame(self.main_frame)
        self.flight_data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.flight_data_tree = ttk.Treeview(self.flight_data_frame, columns=('Airline', 'Departure', 'Arrival', 'Duration', 'Price'))
        self.flight_data_tree.heading('Airline', text='Airline')
        self.flight_data_tree.heading('Departure', text='Departure')
        self.flight_data_tree.heading('Arrival', text='Arrival')
        self.flight_data_tree.heading('Duration', text='Duration')
        self.flight_data_tree.heading('Price', text='Price')
        self.flight_data_tree.pack(fill=tk.BOTH, expand=True)

        self.flight_data_tree.bind('<Double-1>', self.on_flight_selected)
        
    def on_flight_selected(self, event):
        item = self.flight_data_tree.selection()[0]
        flight_data = self.flight_data_tree.item(item, 'values')
        
        self.selection_queue.put(flight_data)
        self.selection_event.set()
        
        if self.flight_data_title.get() == "Departure Flights":
            self.selected_departure = flight_data
            self.flight_data_title.set("Return Flights")
            self.update_flight_data(gfs.load_flight_data('return_flights.json'))
        else:
            self.selected_return = flight_data
            self.calculate_travel_cost()
            
    def update_flight_data(self, flights):
        self.flight_data_tree.delete(*self.flight_data_tree.get_children())
        for flight in flights:
            self.flight_data_tree.insert('', 'end', values=(flight['airline'], flight['departure'], flight['arrival'], flight['duration'], flight['price']))
    
    def display_results(self, results):
        pass
        # Implement this method to show results in the Results tab

    def save_to_csv(self, results):
        pass
        # Implement this method to save results to CSV

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'theme': 'darkly'}  # Default theme

    def change_theme(self, new_theme):
        self.current_theme = new_theme
        self.style.theme_use(new_theme)
            

    def on_tab_change(self, event):
        pass  # We'll keep this method in case you want to add functionality later

    def create_results_tab(self):
        # Table Frame
        table_frame = ttk.Frame(self.results_frame, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure Treeview colors and style
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        # Create the Treeview
        self.tree = ttk.Treeview(table_frame, 
                                columns=('Depart Date', 'Return Date', 'Origin', 'Destination', 
                                        'Flight Price', 'Hotel Cost', 'Car Rental Cost', 'Meal Cost', 
                                        'Number of Days', 'Total Cost', 'Sales Price'), 
                                show='headings')

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
            
    def search_flights(self):
        origin = self.origin_entry.get()
        destination = self.destination_entry.get()
        depart_date = self.departdate_entry.get()
        return_date = self.returndate_entry.get()
        numdays_str = self.days_entry.get()  # Assuming you have this entry in your GUI

        try:
            depart_date, return_date, numdays = tcc.get_travel_dates(depart_date, return_date, numdays_str)
        except ValueError as e:
            messagebox.showerror("Date Error", str(e))
            return

        # Update the GUI entries with the calculated dates
        self.departdate_entry.delete(0, tk.END)
        self.departdate_entry.insert(0, depart_date)
        self.returndate_entry.delete(0, tk.END)
        self.returndate_entry.insert(0, return_date)
        self.days_entry.delete(0, tk.END)
        self.days_entry.insert(0, str(numdays))

        try:
            return_date, depart_date, departure_flights, return_flights = gfs.playwright_gf_scrape(origin, destination, depart_date, return_date)

            gfs.save_flight_data(departure_flights, 'departure_flights.json')
            gfs.save_flight_data(return_flights, 'return_flights.json')

            self.update_flight_data(departure_flights)
            
            # Update the flight data title
            self.flight_data_title.set("Departure Flights")
            
            # Reset selected flights
            self.selected_departure = None
            self.selected_return = None

            messagebox.showinfo("Flight Search", "Flight search completed. Please select a departure flight.")
        except Exception as e:
            messagebox.showerror("Flight Search Error", f"An error occurred while searching for flights: {str(e)}")
            
    def calculate_travel_cost(self):
        if not self.selected_departure or not self.selected_return:
            messagebox.showwarning("Warning", "Please select both departure and return flights.")
            return

        # Use the selected flight data to calculate travel costs
        results = tcc.get_travel_costs(self.selected_departure, self.selected_return, 
                                       self.origin_entry.get(), self.destination_entry.get(),
                                       self.days_entry.get(), self.margin_entry.get(),
                                       self.hotelrate_entry.get(), self.car_rate_entry.get(),
                                       self.meal_cost_entry.get())

        # Display results and save to CSV
        self.display_results(results)
        self.save_to_csv(results)

        # Clear flight data
        gfs.clear_flight_data('departure_flights.json')
        gfs.clear_flight_data('return_flights.json')
    
    
    
    def create_widgets(self):


        # Main Input Frame
        main_input_frame = ttk.Frame(self.main_frame, padding="15")
        main_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left Input Frame
        left_frame = ttk.Frame(main_input_frame)
        left_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 5))

        # Left Frame Contents
        default_origin = tk.StringVar()
        default_origin.set("MCI")

        default_destination = tk.StringVar()
        default_destination.set("DFW")

        ttk.Label(left_frame, text="Origin (airport code):").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=1)
        self.origin_entry = tk.Entry(left_frame, textvariable=default_origin)
        self.origin_entry.grid(row=0, column=1, sticky="ew", pady=1)

        ttk.Label(left_frame, text="Destination (airport code):").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=1)
        self.destination_entry = tk.Entry(left_frame, textvariable=default_destination)
        self.destination_entry.grid(row=1, column=1, sticky="ew", pady=1)

        self.mode_var = tk.BooleanVar(value=False)
        self.mode_checkbox = ttk.Checkbutton(main_input_frame, text="Advanced Mode", variable=self.mode_var, command=self.toggle_mode)
        self.mode_checkbox.pack(side=tk.LEFT, pady=5)

        ttk.Label(left_frame, text="Departure Date:").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=1)
        self.departdate_entry = ttk.Entry(left_frame)
        self.departdate_entry.grid(row=2, column=1, sticky="ew", pady=1)
        ttk.Button(left_frame, text="📅", width=3, command=lambda: self.pick_date(self.departdate_entry)).grid(row=2, column=2, pady=1)

        ttk.Label(left_frame, text="Return Date:").grid(row=3, column=0, sticky="e", padx=(0, 5), pady=1)
        self.returndate_entry = ttk.Entry(left_frame)
        self.returndate_entry.grid(row=3, column=1, sticky="ew", pady=1)
        ttk.Button(left_frame, text="📅", width=3, command=lambda: self.pick_date(self.returndate_entry)).grid(row=3, column=2, pady=1)

        self.optvals_lbl = ttk.Label(left_frame, text="Optional Values (defaults applied if left blank)")
        self.optvals_lbl.grid(row=4, column=0, columnspan=2, sticky="w", pady=1)
        self.optvals_lbl.grid_remove()

        self.days_lbl = ttk.Label(left_frame, text=f"Number of Days (def: {tcc.numdays_std}):")
        self.days_lbl.grid(row=5, column=0, sticky="e", padx=(0, 5), pady=1)
        self.days_lbl.grid_remove()
        
        self.days_entry = ttk.Entry(left_frame)
        self.days_entry.grid(row=5, column=1, sticky="ew", pady=1)
        self.days_entry.grid_remove()

        self.margin_lbl = ttk.Label(left_frame, text=f"Desired Margin (def: {tcc.margin_std}):")
        self.margin_lbl.grid(row=6, column=0, sticky="e", padx=(0, 5), pady=1)
        self.margin_lbl.grid_remove()
        
        self.margin_entry = ttk.Entry(left_frame)
        self.margin_entry.grid(row=6, column=1, sticky="ew", pady=1)
        self.margin_entry.grid_remove()
        

        self.hotelrate_lbl = ttk.Label(left_frame, text=f"Hotel rate (def: ${tcc.hotel_cost_std}):")
        self.hotelrate_lbl.grid(row=7, column=0, sticky="e", padx=(0, 5), pady=1)
        self.hotelrate_lbl.grid_remove()
        
        self.hotelrate_entry = ttk.Entry(left_frame)
        self.hotelrate_entry.grid(row=7, column=1, sticky="ew", pady=1)
        self.hotelrate_entry.grid_remove()

        self.car_rate_lbl = ttk.Label(left_frame, text=f"Rental Cost (def: ${tcc.car_rate_std}):")
        self.car_rate_lbl.grid(row=8, column=0, sticky="e", padx=(0, 5), pady=1)
        self.car_rate_lbl.grid_remove()
        
        self.car_rate_entry = ttk.Entry(left_frame)
        self.car_rate_entry.grid(row=8, column=1, sticky="ew", pady=1)
        self.car_rate_entry.grid_remove()

        self.meal_cost_lbl = ttk.Label(left_frame, text=f"Meal Cost (def: ${tcc.meal_cost_std})")
        self.meal_cost_lbl.grid(row=9, column=0, sticky="e", padx=(0, 5), pady=1)
        self.meal_cost_lbl.grid_remove()
        
        self.meal_cost_entry = ttk.Entry(left_frame)
        self.meal_cost_entry.grid(row=9, column=1, sticky="ew", pady=1)
        self.meal_cost_entry.grid_remove()

        self.main_flight_cost_lbl = ttk.Label(left_frame, text=f"Manual Flight Cost")
        self.main_flight_cost_lbl.grid(row=10, column=0, sticky="e", padx=(0, 5), pady=1)
        self.main_flight_cost_lbl.grid_remove()
        
        self.man_flight_cost_entry = ttk.Entry(left_frame)
        self.man_flight_cost_entry.grid(row=10, column=1, sticky="ew", pady=1)
        self.man_flight_cost_entry.grid_remove()

        # Buttons Frame
        buttons_frame = ttk.Frame(self.main_frame, padding="15")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttons_frame, text="Calculate Costs", style="Calculate.TButton", command=self.calculate_travel_cost).pack(fill=tk.X, padx=5, pady=1)
        ttk.Button(buttons_frame, text="Search for Flights", bootstyle=WARNING, command=self.search_flights).pack(fill=tk.X, padx=5, pady=1)
        
    def check_for_selection_signal(self):
        if self.selection_event.is_set():
            self.selection_event.clear()
            return self.selection_queue.get()
        return None


    def pick_date(self, entry):
        try:
            current_date = datetime.strptime(entry.get(), "%Y-%m-%d").date()
        except ValueError:
            current_date = datetime.now().date()

        cal_dialog = simple_calendar.SimpleCalendar(self, initial_date=current_date)
        self.wait_window(cal_dialog)
        
        if cal_dialog.selected_date:
            entry.delete(0, tk.END)
            entry.insert(0, cal_dialog.selected_date.strftime("%Y-%m-%d"))


    def set_date(self, entry, cal, top):
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    def toggle_mode(self):
        advanced_mode = self.mode_var.get()
        if advanced_mode:
            self.show_advanced_fields()
        else:
            self.hide_advanced_fields()

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
            csvh.delete_from_csv(values)

    def delete_all(self):
            # Ask for confirmation
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all data? This action cannot be undone."):
                # Clear all rows from the Treeview
                for i in self.tree.get_children():
                    self.tree.delete(i)
                
                # Clear all data from the CSV file
                
                try:
                    with open(config.csv_path, '+w', newline='') as csvfile:
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
                        if file.endswith(".json"):
                            os.remove(file)
                    print("All JSON response files have been deleted.")
                except Exception as e:
                    print(f"Error deleting JSON files: {e}")

                messagebox.showinfo("Success", "All data has been deleted successfully.")
               
    def calculate_and_save(self):

        origin = self.origin_entry.get().upper()
        destination = self.destination_entry.get().upper()
        depart_date = self.departdate_entry.get()
        return_date = self.returndate_entry.get()
        numdays_str = self.days_entry.get()
        margin_str = self.margin_entry.get()
        avg_hotel_ntly_str = self.hotelrate_entry.get()
        car_rate_str = self.car_rate_entry.get()
        meal_cost_str = self.meal_cost_entry.get()
        flight_cost_str = self.man_flight_cost_entry.get()

        try:
            self.show_loading_window()
            
            # Run the results function
            results = tcc.get_travel_costs(depart_date, return_date, origin, destination, numdays_str, margin_str, avg_hotel_ntly_str, car_rate_str, meal_cost_str, flight_cost_str)
        
            self.hide_loading_window()
            
            depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price = results
                
        except Exception as e:
            self.hide_loading_window()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        if csvh.log_to_csv(depart_date, return_date, origin, destination, average_flight_price, hotel_cost, car_cost, meal_cost, numdays, total_cost, sales_price):
            messagebox.showinfo("Success", "Data calculated and saved successfully!")
            csvh.load_csv_data(self.tree)  # Refresh the Treeview after saving
            self.flight_data_frame.update_flight_data()
            
        else:
            messagebox.showerror("Error", "Failed to save data to CSV file.")

    def show_advanced_fields(self):
        self.margin_entry.grid()
        self.hotelrate_entry.grid()
        self.car_rate_entry.grid()
        self.meal_cost_entry.grid()
        self.man_flight_cost_entry.grid()
        self.margin_lbl.grid()
        self.hotelrate_lbl.grid()
        self.car_rate_lbl.grid()
        self.meal_cost_lbl.grid()
        self.main_flight_cost_lbl.grid()
        self.days_entry.grid()
        self.days_lbl.grid()

    def hide_advanced_fields(self):
        self.margin_entry.grid_remove()
        self.hotelrate_entry.grid_remove()
        self.car_rate_entry.grid_remove()
        self.meal_cost_entry.grid_remove()
        self.man_flight_cost_entry.grid_remove()
        self.margin_lbl.grid_remove()
        self.hotelrate_lbl.grid_remove()
        self.car_rate_lbl.grid_remove()
        self.meal_cost_lbl.grid_remove()
        self.main_flight_cost_lbl.grid_remove()
        self.days_entry.grid_remove()
        self.days_lbl.grid_remove()