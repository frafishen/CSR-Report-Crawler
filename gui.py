
import tkinter as tk
from tkinter import ttk
import crawler  # Importing functions from crawler.py

# Function to be called when the "Start Process" button is clicked
def start_process():
    year = int(year_entry.get())
    crawler.year = year  # Setting the year in crawler.py
    crawler.run(year)  # Calling the main function from crawler.py
    status_text.delete(1.0, tk.END)
    status_text.insert(tk.END, f"Data processed and saved to table_{year + 1911}.csv")

# Creating main window
root = tk.Tk()
root.title("GUI for Crawler")
root.geometry("600x400")

# Creating input field for year
ttk.Label(root, text="Enter Year:").pack(pady=10)
year_entry = ttk.Entry(root)
year_entry.pack(pady=10)

# Button to start the process
start_button = ttk.Button(root, text="Start Process", command=start_process)
start_button.pack(pady=10)

# Text area to display status messages
status_text = tk.Text(root, height=10, width=50)
status_text.pack(pady=10)

root.mainloop()
