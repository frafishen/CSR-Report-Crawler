"""
Created on Fri. Aug. 18, 2023
@author: Jie-Yu Shen
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
from webOpen import surf


def extract_url_from_row(row, xpaths):
    """Extract the URL from the row using the provided XPaths."""
    for xpath in xpaths:
        try:
            link_element = row.find_element(By.XPATH, xpath)
            return link_element.get_attribute('href')
        except:
            continue
    return None

def getHyperlink(year, _ori, _modified):
    browser = surf(year, 5)

    # Extract table data
    table_element = browser.find_element(By.XPATH, '//*[@id="table01"]/table')
     # Extract all the URLs from the table
    rows = table_element.find_elements(By.XPATH, './tbody/tr')
    xpaths = ['./td[17]/a', './td[12]/a']

    urls = [extract_url_from_row(row, xpaths) for row in rows]

    # Remove empty values from the urls list
    urls = [url for url in urls if url is not None]
    urls = [url for url in urls if url and url[-3:] == 'pdf']


    # # Add the URLs as a new column to the DataFrame
    # df['CSR報告超連結'] = urls

    # Allow some time for the table to load
    time.sleep(5)

    # Close the browser
    browser.quit()

    return urls

def save_urls_to_csv(urls):
    df = pd.read_csv('table_2022.csv', encoding='utf-8')
    # print(len(df))
    # df ['CSR報告超連結'] =  urls
    # df.to_csv('table_2022.csv', index=False)


def main():
    year = 111
    urls = getHyperlink(year)
    print(len(urls))
    df_urls = pd.DataFrame(urls, columns=['CSR報告超連結'], index=None)
    df_urls.to_csv('url_2022.csv', encoding='utf-8')
    # print(len(urls))
    save_urls_to_csv(urls)

if __name__ == "__main__":
    main()