
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
import time
import yaml

# Constants
CONFIG_FILE_PATH = './config.yaml'
CONFIG = None
WEB_PATH = None
DRIVER_PATH = None

def load_config():
    """Load configuration from the YAML file."""
    global CONFIG, WEB_PATH, DRIVER_PATH
    with open(CONFIG_FILE_PATH, 'r') as file:
        CONFIG = yaml.safe_load(file)
    WEB_PATH = CONFIG['CONSTANT']['WEB_PATH']
    DRIVER_PATH = CONFIG['CONSTANT']['DRIVER_PATH']

def surf(year, sec):
    """Open a web page using Selenium, input the given year, and perform a search."""
    load_config()
    chrome_options = Options()
    chrome_options.executable_path = DRIVER_PATH
    browser = webdriver.Chrome(options=chrome_options)

    browser.get(WEB_PATH)

    input_element = browser.find_element(By.XPATH, '//input[@id="year"]')
    input_element.send_keys(year)

    button_element = browser.find_element(By.XPATH, '//input[@type="button" and @value=" 查詢 "]')
    button_element.click()

    time.sleep(sec)

    return browser