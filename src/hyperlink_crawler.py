"""
Hyperlink Crawler Script
------------------------
This script contains functions to crawl a website and extract hyperlink data using Selenium.
Created on Fri. Aug. 22, 2023
@author: Jie-Yu Shen
"""

from selenium.webdriver.common.by import By
import pandas as pd
from webOpen import surf
import time
import yaml

# Constants
CONFIG_FILE_PATH = './config.yaml'
TABLE_PATH = None

def load_config():
    """Load configuration from the YAML file."""
    global TABLE_PATH
    with open(CONFIG_FILE_PATH, 'r') as file:
        config = yaml.safe_load(file)
    TABLE_PATH = config['COMPANY']['TABLE_PATH']

def extract_url_from_row(row, xpaths):
    """Extract the URL from the row using the provided XPaths."""
    for xpath in xpaths:
        try:
            link_element = row.find_element(By.XPATH, xpath)
            return link_element.get_attribute('href')
        except:
            continue
    return None

def extract_hyperlinks_from_table(browser, selected_columns):
    """Extract hyperlinks from a specified table in the browser."""
    table_element = browser.find_element(By.XPATH, '//*[@id="table01"]/table')
    rows = table_element.find_elements(By.XPATH, './tbody/tr')
    xpaths = [f"./td[{selected_columns[0]}]/a", f"./td[{selected_columns[1]}]/a"]
    urls = [extract_url_from_row(row, xpaths) for row in rows]
    return [url for url in urls if url and url.endswith('.pdf')]

def save_hyperlinks_to_csv(year, df_urls):
    """Save the extracted hyperlinks to a CSV file."""
    df_urls.to_csv(f"{TABLE_PATH}url_{year+1911}.csv", encoding='utf-8', index=False)

def merge_hyperlinks_with_table(year):
    """Merge the hyperlinks with the main table and save it to a CSV."""
    main_df = pd.read_csv(f"{TABLE_PATH}table_{year+1911}.csv", encoding='utf-8')
    urls_df = pd.read_csv(f"{TABLE_PATH}url_{year+1911}.csv", encoding='utf-8')
    combined_df = pd.concat([main_df, urls_df], axis=1)
    combined_df.to_csv(f"{TABLE_PATH}table_{year+1911}.csv", encoding='utf-8', index=False)

def format_dataframe(urls, column_name):
    """Format the extracted URLs into a DataFrame."""
    df_urls = pd.DataFrame(urls, columns=[column_name])
    # Adding a header to the DataFrame
    header_row = pd.DataFrame(['CSR報告超連結'], columns=[column_name])
    df_urls = pd.concat([header_row, df_urls]).reset_index(drop=True)
    
    return df_urls

def run(year, selected_columns, len_columns):
    """Main function to run the hyperlink crawler for a specific year."""
    load_config()
    
    # Initialize the browser and extract hyperlinks
    browser = surf(year, 5)
    urls = extract_hyperlinks_from_table(browser, selected_columns)
    browser.quit()
    
    # Prepare the DataFrame for the extracted URLs
    df_urls = format_dataframe(urls, len_columns)
    
    save_hyperlinks_to_csv(year, df_urls)
    merge_hyperlinks_with_table(year)

def main():
    """Main entry point of the script."""
    year = 111
    selected_columns = [12, 17]  # Example columns to select
    run(year, selected_columns)

if __name__ == "__main__":
    main()