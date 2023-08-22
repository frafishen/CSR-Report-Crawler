"""
Created on Fri. Aug. 18, 2023
@author: Jie-Yu Shen
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, yaml

def init():
    global CONFIG, WEB_PATH, DRIVER_PATH
    with open('./config.yaml', 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    WEB_PATH = CONFIG['CONSTANT']['WEB_PATH']
    DRIVER_PATH = CONFIG['CONSTANT']['DRIVER_PATH']


def surf(year, sec):
    init()
# Path to the driver (change this to the location where your driver is)
    chrome_options = Options()
    chrome_options.executable_path = DRIVER_PATH
    browser = webdriver.Chrome(options=chrome_options)

    # Navigate to the webpage
    browser.get(WEB_PATH)

    # Find the input field, enter the year, and submit
    # input_element = browser.find_element(By.ID, 'input_field_id')  # replace 'input_field_id' with the actual ID or another selector
    input_element = browser.find_element(By.XPATH, '//input[@id="year"]')
    input_element.send_keys(year)

    # Locate the button and click on it
    button_element = browser.find_element(By.XPATH, '//input[@type="button" and @value=" 查詢 "]')
    button_element.click()

    # Allow some time for the table to load
    time.sleep(sec)

    return browser

