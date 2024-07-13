import tkinter as tk
from tkinter import ttk, messagebox
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SettingsTab(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.parent = parent
        self.main_app = main_app
        self.settings = self.load_settings()
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Theme:").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=5)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', self.main_app.current_theme))
        
        # Get all available ttkbootstrap themes
        all_themes = list(self.main_app.style.theme_names())
        
        self.theme_combobox = ttk.Combobox(self, textvariable=self.theme_var, values=all_themes)
        self.theme_combobox.grid(row=0, column=1, sticky="ew", pady=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)
        
        ttk.Button(self, text="Load Flight Data", command=self.main_app.open_flight_data).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Save Settings", command=self.save_settings).grid(row=1, column=0, columnspan=2, pady=10)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'theme': 'cosmo'}  # Default theme

    def save_settings(self):
        self.settings['theme'] = self.theme_var.get()
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
        self.main_app.change_theme(self.settings['theme'])
        messagebox.showinfo("Success", "Settings saved successfully!")

    def change_theme(self, event=None):
        new_theme = self.theme_var.get()
        self.main_app.change_theme(new_theme)

    def reset_password(self):
        # Implement password reset logic here
        pass

    def logout(self):
        self.main_app.reset_settings_tab()
        self.main_app.notebook.select(0)  # Switch to main tab