"""
Created on Fri. Aug. 18, 2023
@author: Jie-Yu Shen
"""

import tkinter as tk
from tkinter import ttk, Canvas, Frame, Scrollbar
import os, csv, yaml
import crawler  # Importing functions from crawler.py
import hyperlink_crawler as hc  # Importing functions from hyperlink_crawler.py
import report_download as dl  # Importing functions from download.py

def init():
    global CONFIG, TABLE_PATH, ROOT_PATH, PDF_DIR, JPG_DIR
    with open('./config.yaml', 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    TABLE_PATH = CONFIG['COMPANY']['TABLE_PATH']
    ROOT_PATH = CONFIG['SAVE']['ROOT_DIR']
    PDF_DIR = CONFIG['SAVE']['PDF_DIR']
    JPG_DIR = CONFIG['SAVE']['IMG_DIR']

clicked_buttons = [] 
init()

def ok_clicked(flag):
    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, "OK button clicked.")
    print("OK button clicked.")

    year = int(year_entry.get())

    dl.run(year+1911, flag)
    status_text.insert(tk.END, "\n")
    status_text.insert(tk.END, "Download Completed.")

def reset_clicked():
    global clicked_buttons
    clicked_buttons.clear()
    print("Reset button clicked.")

def link_clicked():
    status_text.insert(tk.END, f"selected columns' id: {clicked_buttons}")
    print("\"Get Link\" button clicked.")
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
    status_text.insert(tk.END, f"Data processed and saved to {TABLE_PATH}table_{year + 1911}.csv")


def start_process():
    year = int(year_entry.get())
    headers_path = f"{TABLE_PATH}header_row_{year+1911}.csv"

    get_table()
    display_csv_buttons(headers_path)


required_dirs = [ROOT_PATH, JPG_DIR, PDF_DIR, TABLE_PATH]
for dir_name in required_dirs:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

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
start_button = ttk.Button(root, text="1. Start Process", command=start_process)
start_button.pack(pady=10)

# Text area to display status messages
status_text = tk.Text(root, height=8, width=50)
status_text.pack(pady=10)

# Frame for Reset and OK buttons
buttons_control_frame_1 = Frame(root)
buttons_control_frame_1.pack(pady=10)
reset_button = ttk.Button(buttons_control_frame_1, text="Reset", command=reset_clicked)
reset_button.pack(side=tk.LEFT, padx=10)
link_button = ttk.Button(buttons_control_frame_1, text="2. Get Link", command=link_clicked)
link_button.pack(side=tk.LEFT, padx=10)

# Create a new frame below the previous frame for the new buttons
buttons_control_frame_2 = Frame(root)
buttons_control_frame_2.pack(pady=10)

# Create the "Test" button and pack it to the left within the new frame
test_button = ttk.Button(buttons_control_frame_2, text="3. Test", command=lambda: ok_clicked(0))
test_button.pack(side=tk.LEFT, padx=10)

# Create the "Get All Report" button and pack it to the left within the new frame
get_all_report_button = ttk.Button(buttons_control_frame_2, text="4. Get All Report", command=lambda: ok_clicked(1))
get_all_report_button.pack(side=tk.LEFT, padx=10)


root.mainloop()


