
"""
Web Open Script
---------------
This script contains functions to open web pages using Selenium and perform specific actions.
Created on Fri. Aug. 22, 2023
@author: Jie-Yu Shen
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import yaml
import os

# Constants
CONFIG_FILE_PATH = './config.yaml'
CONFIG = None
WEB_PATH = None
DRIVER_PATH = None

cat_id = ''

choices_mapping = {
    '上市': 'sii',
    '上櫃': 'otc',
    '興櫃': 'rotc',
    '公開發行': 'pub'
}

def load_config(cat_entry):
    """Load configurations from the config file."""
    # Determine the directory of the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to config.yaml
    config_path = os.path.join(script_dir, CONFIG_FILE_PATH)
    global CONFIG, WEB_PATH, DRIVER_PATH, cat_id
    with open(config_path, 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    WEB_PATH = CONFIG['CONSTANT']['WEB_PATH']
    # DRIVER_PATH = CONFIG['CONSTANT']['DRIVER_PATH']
    cat_id = choices_mapping[cat_entry]

def surf(year, cat_entry, sec):
    """Open a web page using Selenium, input the given year, and perform a search."""
    load_config(cat_entry)
    chrome_options = Options()
    # chrome_options.executable_path = DRIVER_PATH
    chrome_options.executable_path = ChromeDriverManager().install()
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(WEB_PATH)

    # Select the dropdown based on cat_id
    select_element = Select(browser.find_element(By.XPATH, "//*[@id='search']/table/tbody/tr/td[3]/select"))
    select_element.select_by_value(str(cat_id))

    time.sleep(3)

    input_element = browser.find_element(By.XPATH, '//input[@id="year"]')
    input_element.send_keys(year)

    button_element = browser.find_element(By.XPATH, '//input[@type="button" and @value=" 查詢 "]')
    

    button_element.click()

    time.sleep(sec)

    return browser

