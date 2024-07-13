import calendar
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class SimpleCalendar(tk.Toplevel):
    def __init__(self, parent, initial_date=None):
        super().__init__(parent)
        self.parent = parent
        self.title("Select Date")
        self.geometry("300x250")
        self.resizable(False, False)

        self.selected_date = initial_date or datetime.now().date()

        self.year_var = tk.StringVar(value=str(self.selected_date.year))
        self.month_var = tk.StringVar(value=str(self.selected_date.month))

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self, textvariable=self.year_var, width=6).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Month:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Combobox(self, textvariable=self.month_var, values=[str(i) for i in range(1, 13)], width=4).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(self, text="Show Calendar", command=self.update_calendar).grid(row=0, column=4, padx=5, pady=5)

        self.cal_frame = ttk.Frame(self)
        self.cal_frame.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        self.update_calendar()

    def update_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        year = int(self.year_var.get())
        month = int(self.month_var.get())

        cal = calendar.monthcalendar(year, month)

        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(self.cal_frame, text=day).grid(row=0, column=i)

        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = ttk.Button(self.cal_frame, text=str(day), width=4,
                                     command=lambda d=day: self.select_date(year, month, d))
                    btn.grid(row=week_num, column=day_num)

    def select_date(self, year, month, day):
        self.selected_date = datetime(year, month, day).date()
        self.destroy()