"""
Created on Fri. Aug. 18, 2023
@author: Jie-Yu Shen
"""

from selenium.webdriver.common.by import By
import pandas as pd
from webOpen import surf
import time, yaml

def init():
    global CONFIG, TABLE_PATH
    with open('./config.yaml', 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    TABLE_PATH = CONFIG['COMPANY']['TABLE_PATH']

def extract_url_from_row(row, xpaths):
    """Extract the URL from the row using the provided XPaths."""
    for xpath in xpaths:
        try:
            link_element = row.find_element(By.XPATH, xpath)
            return link_element.get_attribute('href')
        except:
            continue
    return None

def getHyperlink(year: int, selected_columns: list[str, str]) -> list[str]:
    _ori = selected_columns[0]
    _modified = selected_columns[1]

    browser = surf(year, 5)

    # Extract table data
    table_element = browser.find_element(By.XPATH, '//*[@id="table01"]/table')
     # Extract all the URLs from the table
    rows = table_element.find_elements(By.XPATH, './tbody/tr')
    xpaths = [f"./td[{_ori}]/a", f"./td[{_modified}]/a"]

    urls = [extract_url_from_row(row, xpaths) for row in rows]

    # Remove empty values from the urls list
    urls = [url for url in urls if url is not None]
    urls = [url for url in urls if url and url[-3:] == 'pdf']

    # Allow some time for the table to load
    time.sleep(5)

    # Close the browser
    browser.quit()

    return urls

def save_urls_to_csv(year):
    df = pd.read_csv(f"{TABLE_PATH}table_{year+1911}.csv", encoding='utf-8')
    df_urls = pd.read_csv(f"{TABLE_PATH}url_{year+1911}.csv", encoding='utf-8')
    print(f"len of table: {len(df)}")
    print(f"len of df_urls: {len(df_urls)}")
    df = pd.concat([df, df_urls], axis=1, ignore_index=True)
    df.to_csv(f"{TABLE_PATH}table_{year+1911}.csv", encoding='utf-8', index=False)



def run(year, selected_columns, len_columns):
    init()

    urls = getHyperlink(year, selected_columns)
    df_urls = pd.DataFrame(urls, columns=['CSR報告超連結'], index=None)

    df_urls.columns = [len_columns]
    df_urls.loc[-1] = ['CSR報告超連結']  
    df_urls.index = df_urls.index + 1 
    df_urls = df_urls.sort_index()  
    
    TABLE_PATH = CONFIG['COMPANY']['TABLE_PATH']
    df_urls.to_csv(f"{TABLE_PATH}url_{year+1911}.csv", encoding='utf-8', index=False)
    save_urls_to_csv(year)

def main():
    year = 111
    urls = getHyperlink(year)
    df_urls = pd.DataFrame(urls, columns=['CSR報告超連結'], index=None)
    df_urls.to_csv('url_2022.csv', encoding='utf-8')
    save_urls_to_csv(urls)

if __name__ == "__main__":
    main()