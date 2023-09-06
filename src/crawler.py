"""
Crawler Script
---------------
This script contains functions to crawl a website and extract table data using Selenium and BeautifulSoup.
Created on Fri. Aug. 22, 2023
@author: Jie-Yu Shen
"""

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import os
from webOpen import surf

# Constants
CONFIG_FILE_PATH = './config.yaml'
TIMESTAMP_DIR, ROOT_PATH, TABLE_PATH, cat_entry = '', '', '', ''
year = 111

def set_year(year: int) -> None:
    """Set the year to be crawled."""
    year = year

def load_config(TIMESTAMP_DIR, cat_entry):
    """Load configurations from the config file."""
    # Determine the directory of the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to config.yaml
    config_path = os.path.join(script_dir, CONFIG_FILE_PATH)
    global TABLE_PATH
    with open(config_path, 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    TABLE_PATH = os.path.join(TIMESTAMP_DIR, cat_entry, CONFIG['COMPANY']['TABLE_PATH'])

def merge_header_cells(header_html: str) -> list[str]:
    """Merge header cells for tables with two rows of headers."""
    soup = BeautifulSoup(header_html, "html.parser")
    rows = soup.find_all("tr")
    if len(rows) == 1:
        return [cell.get_text(strip=True) for cell in rows[0].find_all("td")]

    primary_header_cells = rows[0].find_all("td")
    secondary_header_cells = rows[1].find_all("td")
    merged_header = []
    secondary_index = 0
    for cell in primary_header_cells:
        primary_text = cell.get_text(strip=True)
        colspan = int(cell.get("colspan", 1))
        if colspan == 1:
            merged_header.append(primary_text)
        else:
            for _ in range(colspan):
                merged_header.append(f"{primary_text}({secondary_header_cells[secondary_index].get_text(strip=True)})")
                secondary_index += 1
    return merged_header

def extract_table_data(browser, year: int) -> pd.DataFrame:
    """Extract table data from the website for a given year."""
    # Get the first two header rows with the class 'tblHead'
    header_row_elements = browser.find_elements(By.XPATH, '//*[@id="table01"]/table/tbody/tr[contains(@class, "tblHead")]')[:2]
    header_rows_html = [elem.get_attribute('outerHTML') for elem in header_row_elements]
    combined_header_html = "".join(header_rows_html)

    # Use the merge_header_cells function to process combined_header_html
    merged_header = merge_header_cells(combined_header_html)
    additional_columns = ['公司完整名稱', '統一編號']
    additional_columns_df = pd.DataFrame(additional_columns).T
    header_df = pd.DataFrame([merged_header])
    header_df = pd.concat([header_df, additional_columns_df], axis=1, ignore_index=True)

    header_df.to_csv(f"{TABLE_PATH}header_row_{year+1911}.csv", index=False)

    table_rows = browser.find_elements(By.XPATH, '//*[@id="table01"]/table/tbody/tr[contains(@class, "odd") or contains(@class, "even")]')
    rows_html = [row.get_attribute('outerHTML') for row in table_rows]
    table_html = "<table>" + "".join(rows_html) + "</table>"
    df_rows = pd.read_html(table_html)[0]

    combined_df = pd.concat([header_df, df_rows], axis=0, ignore_index=True)
    return combined_df

def get_table_for_year(year: int, cat_entry: str) -> pd.DataFrame:
    """Get table data for a specific year."""
    browser = surf(year, cat_entry, 10)
    data_frame = extract_table_data(browser, year)
    browser.quit()
    return data_frame

def run(year: int, TIMESTAMP_DIR: str, cat_entry: str) -> int:
    """Main function to run the crawler for a specific year."""
    load_config(TIMESTAMP_DIR, cat_entry)
    result = get_table_for_year(year, cat_entry)
    result.to_csv(f"{TABLE_PATH}table_{year+1911}.csv", encoding='utf-8', index=False)
    return result.shape[1]

def main():
    """Main entry point of the script."""
    year = 111
    result = get_table_for_year(year)
    result.to_csv("../output/table/table_{}.csv".format(year+1911), encoding='utf-8', index=False)

if __name__ == "__main__":
    main()
