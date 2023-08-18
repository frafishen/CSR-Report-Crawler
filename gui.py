"""
Created on Fri. Aug. 18, 2023
@author: Jie-Yu Shen
"""

import tkinter as tk
from tkinter import ttk, Canvas, Frame, Scrollbar
import csv 
import crawler  # Importing functions from crawler.py
import hyperlink_crawler as hc  # Importing functions from hyperlink_crawler.py

clicked_buttons = [] 

def reset_clicked():
    global clicked_buttons
    clicked_buttons.clear()
    print("Reset button clicked.")

def ok_clicked():
    status_text.insert(tk.END, f"selected columns' id: {clicked_buttons}")
    print("OK button clicked.")
    year = int(year_entry.get())
    hc.run(year, clicked_buttons, num_cols)
    
    reset_clicked()

    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, "Hyperlink Crawling Completed.")

def button_clicked(button_id):
    print(button_id)
    clicked_buttons.append(button_id)
    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, f"selected columns' id: {clicked_buttons}")

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
            
            button = ttk.Button(buttons_frame, text=header)
            button.grid(row=row, column=col, padx=5, pady=5)
            button.bind("<Button-1>", lambda event, id=i+1: button_clicked(id))

    buttons_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to be called when the "Start Process" button is clicked
def get_table():
    year = int(year_entry.get())
    crawler.year = year  # Setting the year in crawler.py
    global num_cols
    num_cols = crawler.run(year)  # Calling the main function from crawler.py
    status_text.delete(1.0, tk.END)
    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, f"Number of columns: {num_cols}")
    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, f"Data processed and saved to table_{year + 1911}.csv")


def start_process():
    year = int(year_entry.get())
    headers_path = f"./output/table/header_row_{year+1911}.csv"

    get_table()
    display_csv_buttons(headers_path)

# Creating main window
root = tk.Tk()
root.title("CSR Report Crawler")
root.geometry("1200x600")

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
status_text = tk.Text(root, height=8, width=50)
status_text.pack(pady=10)

# Frame for Reset and OK buttons
buttons_control_frame = Frame(root)
buttons_control_frame.pack(pady=10)
reset_button = ttk.Button(buttons_control_frame, text="Reset", command=reset_clicked)
reset_button.pack(side=tk.LEFT, padx=10)
ok_button = ttk.Button(buttons_control_frame, text="OK", command=ok_clicked)
ok_button.pack(side=tk.LEFT, padx=10)

root.mainloop()


