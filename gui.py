"""
Created on Fri. Aug. 18, 2023
@author: Jenny Shen
"""

import tkinter as tk
from tkinter import ttk, Canvas, Frame, Scrollbar
import csv 
import crawler  # Importing functions from crawler.py


def display_csv_buttons(csv_path):
    global buttons_frame
    if "buttons_frame" in globals():
        buttons_frame.destroy()
    buttons_frame = Frame(canvas)
    canvas.create_window((0,0), window=buttons_frame, anchor="nw")
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first row
        headers = next(reader)
        for i, header in enumerate(headers):
            row, col = divmod(i, 5)
            ttk.Button(buttons_frame, text=header).grid(row=row, column=col, padx=5, pady=5)
    buttons_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to be called when the "Start Process" button is clicked
def get_table():
    year = int(year_entry.get())
    crawler.year = year  # Setting the year in crawler.py
    crawler.run(year)  # Calling the main function from crawler.py
    status_text.delete(1.0, tk.END)
    status_text.insert(tk.END, f"Data processed and saved to table_{year + 1911}.csv")

def start_process():
    year = int(year_entry.get())
    headers_path = f"./output/table/header_row_{year+1911}.csv"

    get_table()
    display_csv_buttons(headers_path)

# Creating main window
root = tk.Tk()
root.title("GUI for Crawler")
root.geometry("1200x500")

canvas = Canvas(root)
canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

# Creating input field for year
ttk.Label(root, text="Enter Year:").pack(pady=10)
year_entry = ttk.Entry(root)
year_entry.pack(pady=10)

# Button to start the process
start_button = ttk.Button(root, text="Start Process", command=start_process)
start_button.pack(pady=10)

# Text area to display status messages
status_text = tk.Text(root, height=5, width=50)
status_text.pack(pady=10)

root.mainloop()
