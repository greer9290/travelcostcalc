import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os, csv, json, subprocess
from src import config
import webbrowser
from PIL import Image, ImageTk

class FlightDataTab(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

        self.title_label = ttk.Label(self, textvariable=main_app.flight_data_title)
        self.title_label.pack(pady=10)

    def setup_treeview_sorting(self):
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(_col, False))

    def on_flight_double_click(self, event):
        item = self.tree.selection()[0]
        link = self.tree.item(item, "values")[-1]
        if link:
            webbrowser.open(link)

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))
            
    def debug_treeview(self):
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            image = self.tree.item(item, 'image')
            print(f"Item: {item}, Values: {values}, Image: {image}")

    def load_airline_logo(self, item, airline):
        # Simplify airline name for filename
        simple_airline_name = ''.join(c.lower() for c in airline if c.isalnum())
        logo_path = os.path.join(os.path.dirname(__file__), "logos", f"{simple_airline_name}.png")
        print(f"Looking for logo: {logo_path}")

        if not os.path.exists(logo_path):
            print(f"Logo not found for {airline}")
            return

        try:
            with Image.open(logo_path) as img:
                # Resize the image to a smaller size
                img_resized = img.resize((90, 40), Image.Resampling.LANCZOS)
                
                # Convert to RGB if it's RGBA
                if img_resized.mode == 'RGBA':
                    img_resized = img_resized.convert('RGB')

                # Convert to PhotoImage
                logo = ImageTk.PhotoImage(img_resized)

                # Store reference to avoid garbage collection
                self.logo_images[item] = logo

                # Update the Treeview item
                self.tree.set(item, 'Logo', '')  # Clear any text in the Logo column
                self.tree.item(item, image=logo)

                print(f"Logo loaded for {airline}")
                print(f"PhotoImage size: {logo.width()} x {logo.height()}")
                print(f"Treeview item image: {self.tree.item(item, 'image')}")
                
                # After loading all logos
                self.tree.update()

        except Exception as e:
            print(f"Error loading logo for {airline}: {str(e)}")


    def open_flight_data(self):
        print("Attempting to Open Flight Data")
        print("Flight path opened")
        if os.path.exists(config.json_flight_path):
            if os.name == 'nt':  # For Windows
                os.startfile(config.json_flight_path)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.call(('open', config.json_flight_path))
            else:
                messagebox.showerror("Error", "Unsupported operating system")
        else:
            messagebox.showerror("Error", "Flight data file not found")