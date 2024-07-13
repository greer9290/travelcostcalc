# src/gui/main_window.py


from tkinter import ttk, messagebox
import csv
from datetime import datetime
import os
from ttkbootstrap import Style
import subprocess



import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ttkbootstrap import Style
from gui.settings_tab import SettingsTab
from gui.simple_calendar import SimpleCalendar
import travel_cost_calculator as tcc
import os
from travel_cost_calculator import get_travel_costs
from csv_handler import log_to_csv, load_csv_data, delete_from_csv

class TravelCostApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Travel Cost Calculator")
        self.state('zoomed')

        self.style = Style(theme="flatly")
        self.current_theme = "flatly"

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Travel Cost Calculator")

        self.create_widgets()

        self.settings_frame = SettingsTab(self.notebook, self)
        self.notebook.add(self.settings_frame, text="Settings")

    def load_csv_data(self):
            load_csv_data(self.tree)

    def on_tab_change(self, event):
        pass  # We'll keep this method in case you want to add functionality later

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

    def open_flight_data(self):
        file_path = 'google_flight_results.json'
        if os.path.exists(file_path):
            if os.name == 'nt':  # For Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.call(('open', file_path))
            else:
                messagebox.showerror("Error", "Unsupported operating system")
        else:
            messagebox.showerror("Error", "Flight data file not found")
    
    def create_widgets(self):


        # Main Input Frame
        main_input_frame = ttk.Frame(self.main_frame, padding="15")
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
        self.mode_checkbox.pack(side=tk.TOP, pady=5)

        ttk.Label(left_frame, text="Departure Date:").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=1)
        self.departdate_entry = ttk.Entry(left_frame)
        self.departdate_entry.grid(row=2, column=1, sticky="ew", pady=1)
        ttk.Button(left_frame, text="📅", width=3, command=lambda: self.pick_date(self.departdate_entry)).grid(row=2, column=2, pady=1)

        ttk.Label(left_frame, text="Return Date:").grid(row=3, column=0, sticky="e", padx=(0, 5), pady=1)
        self.returndate_entry = ttk.Entry(left_frame)
        self.returndate_entry.grid(row=3, column=1, sticky="ew", pady=1)
        ttk.Button(left_frame, text="📅", width=3, command=lambda: self.pick_date(self.returndate_entry)).grid(row=3, column=2, pady=1)

        # Right Frame Contents
        ttk.Label(right_frame, text="Optional Values (defaults applied if left blank)").grid(row=0, column=0, columnspan=2, sticky="w", pady=1)

        ttk.Label(right_frame, text=f"Number of Days (def: {tcc.numdays_std}):").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=1)
        self.days_entry = ttk.Entry(right_frame)
        self.days_entry.grid(row=1, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Desired Margin (def: {tcc.margin_std}):").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=1)
        self.margin_entry = ttk.Entry(right_frame)
        self.margin_entry.grid(row=2, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Hotel rate (def: ${tcc.hotel_cost_std}):").grid(row=3, column=0, sticky="e", padx=(0, 5), pady=1)
        self.hotelrate_entry = ttk.Entry(right_frame)
        self.hotelrate_entry.grid(row=3, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Rental Cost (def: ${tcc.car_rate_std}):").grid(row=4, column=0, sticky="e", padx=(0, 5), pady=1)
        self.car_rate_entry = ttk.Entry(right_frame)
        self.car_rate_entry.grid(row=4, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Meal Cost (def: ${tcc.meal_cost_std})").grid(row=5, column=0, sticky="e", padx=(0, 5), pady=1)
        self.meal_cost_entry = ttk.Entry(right_frame)
        self.meal_cost_entry.grid(row=5, column=1, sticky="ew", pady=1)

        ttk.Label(right_frame, text=f"Manual Flight Cost").grid(row=6, column=0, sticky="e", padx=(0, 5), pady=1)
        self.man_flight_cost_entry = ttk.Entry(right_frame)
        self.man_flight_cost_entry.grid(row=6, column=1, sticky="ew", pady=1)

        # Buttons Frame
        buttons_frame = ttk.Frame(self.main_frame, padding="15")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttons_frame, text="Calculate", style="Calculate.TButton", command=self.calculate_and_save).pack(fill=tk.X, padx=5, pady=1)
        ttk.Button(buttons_frame, text="Delete Selected", style="Delete.TButton", command=self.delete_selected).pack(fill=tk.X, padx=5, pady=1)
        ttk.Button(buttons_frame, text="Delete All Items", style="DeleteAll.TButton", command=self.delete_all).pack(fill=tk.X, padx=5, pady=1)

        # Table Frame
        table_frame = ttk.Frame(self.main_frame, padding="10")
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
        
        self.load_csv_data()

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
    

    def pick_date(self, entry):
        try:
            current_date = datetime.strptime(entry.get(), "%Y-%m-%d").date()
        except ValueError:
            current_date = datetime.now().date()

        cal_dialog = SimpleCalendar(self, initial_date=current_date)
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

    def create_settings_frame(self):
        if self.settings_frame is None:
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if self.check_password(password):
                # Remove the dummy settings tab
                self.notebook.forget(self.dummy_settings_frame)
                
                # Create and add the actual settings frame
                self.settings_frame = SettingsTab(self.notebook, self)
                self.notebook.add(self.settings_frame, text="Settings")
                self.settings_tab_created = True  # Set the flag
            else:
                messagebox.showerror("Error", "Incorrect password")
                self.notebook.select(0)  # Switch back to main tab


    def reset_settings_tab(self):
        if self.settings_frame:
            self.notebook.forget(self.settings_frame)
            self.settings_frame = None
            self.settings_tab_created = False  # Reset the flag
            
            # Add back the dummy settings tab
            self.dummy_settings_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.dummy_settings_frame, text="Settings")

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
            delete_from_csv(values)

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
            results = get_travel_costs(depart_date, return_date, origin, destination, numdays_str, margin_str, avg_hotel_ntly_str, car_rate_str, meal_cost_str, flight_cost_str)
        
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

    def show_advanced_fields(self):
        self.margin_entry.grid()
        self.hotelrate_entry.grid()
        self.car_rate_entry.grid()
        self.meal_cost_entry.grid()
        self.man_flight_cost_entry.grid()

    def hide_advanced_fields(self):
        self.margin_entry.grid_remove()
        self.hotelrate_entry.grid_remove()
        self.car_rate_entry.grid_remove()
        self.meal_cost_entry.grid_remove()
        self.man_flight_cost_entry.grid_remove()