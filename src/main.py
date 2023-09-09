"""
Crawler Script
---------------
This script contains functions to crawl a website and extract table data using Selenium and BeautifulSoup.
Created on Fri. Aug. 23, 2023
@author: Jie-Yu Shen
"""

# Imports

# Standard Libraries
import os
import csv
import yaml
from datetime import datetime
import sys
import wx

# Custom Modules
import crawler
import hyperlink_crawler as hc
import report_download as dl

# Global Variables and Constants
CONFIG = {}
TIMESTAMP_DIR, TABLE_PATH, ROOT_PATH, PDF_DIR, JPG_DIR, prefix_path = '', '', '', '', '', ''
clicked_buttons = []
cat_entry = '上市'  # Default value for the dropdown menu

# Functions

def get_current_timestamp():
    """Generate a timestamp in the format yymmdd_HHMM."""
    now = datetime.now()
    return now.strftime('%y%m%d_%H%M')

def initialize_config():
    """Load configurations from the config file."""
    # Determine the directory of the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to config.yaml
    config_path = os.path.join(script_dir, 'config.yaml')
    
    global CONFIG, TABLE_PATH, ROOT_PATH, PDF_DIR, JPG_DIR, TIMESTAMP_DIR, prefix_path
    with open(config_path, 'r') as file:
        CONFIG = yaml.safe_load(file)

    # Generate folder name based on current date and time
    timestamp = get_current_timestamp()
    ROOT_PATH = os.path.join(script_dir, CONFIG['SAVE']['ROOT_DIR'])
    TIMESTAMP_DIR = os.path.join(ROOT_PATH, timestamp)
    
    prefix_path = f"{TIMESTAMP_DIR}_{cat_entry}"
    TABLE_PATH = os.path.join(prefix_path, CONFIG['COMPANY']['TABLE_PATH'])
    PDF_DIR = os.path.join(prefix_path, CONFIG['SAVE']['PDF_DIR'])
    JPG_DIR = os.path.join(prefix_path, CONFIG['SAVE']['IMG_DIR'])

    required_dirs = [ROOT_PATH, JPG_DIR, PDF_DIR, TABLE_PATH]
    print("建立資料夾名稱")
    print(required_dirs)
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def create_folders(event):
    """Create the necessary folders for saving the data."""
    initialize_config()
    status_text.AppendText("Folder Create Complete.")

def on_dropdown_change(event):
    global cat_entry
    cat_entry = event.GetEventObject().GetStringSelection()

def start_process(cat_entry):
    year = int(year_entry.GetValue())
    csv_path = f"{TABLE_PATH}table_{year + 1911}.csv"
    get_table(cat_entry)
    display_csv_buttons(csv_path)

def ok_clicked(flag):
    status_text.AppendText("\nOK button clicked.")
    year = int(year_entry.GetValue())
    dl.run(year + 1911, flag, cat_entry, prefix_path)
    status_text.AppendText("\nDownload process completed.")

def reset_clicked():
    global clicked_buttons
    clicked_buttons.clear()
    print("Reset button clicked.")

def link_clicked():
    status_text.AppendText("\n" + ", ".join(map(str, clicked_buttons)))
    year = int(year_entry.GetValue())
    hc.run(year, clicked_buttons, len(clicked_buttons), prefix_path, cat_entry)
    reset_clicked()
    status_text.AppendText("\nHyperlink crawling process completed.")

def button_clicked(button_id):
    clicked_buttons.append(button_id+1)
    status_text.AppendText("\n" + ", ".join(map(str, clicked_buttons)))

def display_csv_buttons(csv_path):
    global buttons_frame
    if 'buttons_frame' in globals():
        buttons_frame.Destroy()
    buttons_frame = wx.ScrolledWindow(canvas, size=(1160, 500))
    buttons_frame.SetPosition((10, 80))
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first row
        headers = next(reader)
        for idx, header in enumerate(headers):
            if(idx == 11):
                button = wx.Button(buttons_frame, label=str(2)+". "+header)
            elif(idx == 16):
                button = wx.Button(buttons_frame, label=str(3)+". "+header)
            else:
                button = wx.Button(buttons_frame, label=header)
            button.Bind(wx.EVT_BUTTON, lambda evt, button_id=idx: button_clicked(button_id))
            row, col = divmod(idx, 5)
            button.SetPosition((col * 220, row * 40))
        
    buttons_frame.SetScrollbars(20, 20, len(headers) // 5 * 220, len(headers) * 40)



def get_table(cat_entry):
    year = int(year_entry.GetValue())
    crawler.set_year(year)
    crawler.run(year, prefix_path, cat_entry)
    status_text.Clear()
    status_text.AppendText(f"{len(clicked_buttons)} columns processed.")
    status_text.AppendText(f"\nData saved at {TABLE_PATH}table_{year + 1911}.csv")

def setup_gui():
    global year_entry, status_text, canvas

    app = wx.App(False)
    root = wx.Frame(None, title="CSR Report Crawler", size=(1200, 600))
    canvas = wx.Panel(root, size=(1200, 600))
    
    year_label = wx.StaticText(canvas, label="Year:", pos=(10, 10))
    year_entry = wx.TextCtrl(canvas, pos=(60, 10), size=(100, -1))
    choices = ['上市', '上櫃', '興櫃', '公開發行']
    dropdown = wx.ComboBox(canvas, pos=(170, 10), choices=choices, style=wx.CB_READONLY)
    dropdown.SetSelection(0)
    dropdown.Bind(wx.EVT_COMBOBOX, lambda evt: on_dropdown_change(evt))

    def start_button_handler(evt):
        selected_value = dropdown.GetStringSelection()
        start_process(selected_value)
    
    check_setting_button = wx.Button(canvas, wx.ID_ANY, "0. Create Folders", pos=(300, 10))
    check_setting_button.Bind(wx.EVT_BUTTON, create_folders)

    start_process_button = wx.Button(canvas, label="1. Start Process!", pos=(430, 10))
    start_process_button.Bind(wx.EVT_BUTTON, start_button_handler)
    
    reset_button = wx.Button(canvas, label="Reset", pos=(560, 10))
    reset_button.Bind(wx.EVT_BUTTON, lambda evt: reset_clicked())
    
    link_button = wx.Button(canvas, label="4. Get Link", pos=(650, 10))
    link_button.Bind(wx.EVT_BUTTON, lambda evt: link_clicked())

    get_all_report_button = wx.Button(canvas, label="5. Get All Report and Covers", pos=(750, 10))
    get_all_report_button.Bind(wx.EVT_BUTTON, lambda evt: ok_clicked(1))

    status_text = wx.TextCtrl(canvas, pos=(10, 350), size=(1170, 210), style=wx.TE_MULTILINE)

    root.Show(True)
    app.MainLoop()


# Main Execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_directory = sys.argv[1]
    else:
        base_directory = os.path.dirname(os.path.abspath(__file__))
        
    # Ensure necessary directories exist
    setup_gui()
