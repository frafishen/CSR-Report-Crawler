"""
Created on Fri. Aug. 18, 2023
@author: Jenny Shen
"""

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from webOpen import surf

# pip install bs4
# pip install html5lib

def merge_header_cells(header_html: str) -> (list[str] | list):
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

def get_table_for_year(year: int) -> pd.DataFrame:
    browser = surf(year, 5)

    # Extract table data
    # Locate the table and extract its data

    # Get the first two header rows with the class 'tblHead'
    header_row_elements = browser.find_elements(By.XPATH, '//*[@id="table01"]/table/tbody/tr[contains(@class, "tblHead")]')[:2]
    header_rows_html = [elem.get_attribute('outerHTML') for elem in header_row_elements]
    combined_header_html = "".join(header_rows_html)

    # Use the merge_header_cells function to process combined_header_html
    merged_header = merge_header_cells(combined_header_html)
    add_col_list = ['CSR報告超連結', '公司完整名稱', '統一編號']
    add_col_df = pd.DataFrame(add_col_list).T
    header_df = pd.DataFrame([merged_header])
    header_df = pd.concat([header_df,add_col_df], axis=1, ignore_index=True)

    # # Parse header_row_html to extract data
    # header_df = pd.read_html(f"<table>{header_row_html}</table>")[0]
    # Handle <br> elements to separate data and save to CSV
    header_df.to_csv("./output/table/header_row_{}.csv".format(year+1911), index=False)

    table_rows = browser.find_elements(By.XPATH, '//*[@id="table01"]/table/tbody/tr[contains(@class, "odd") or contains(@class, "even")]')
    rows_html = [row.get_attribute('outerHTML') for row in table_rows]
    table_html = "<table>" + "".join(rows_html) + "</table>"
    df_rows = pd.read_html(table_html)[0]

    df = pd.concat([header_df, df_rows], axis=0, ignore_index=True)
    # Close the browser
    browser.quit()

    return df


def run(year):
    result = get_table_for_year(year)
    result.to_csv("./output/table/table_{}.csv".format(year+1911), encoding='utf-8', index=False)

def main():
    year = 111
    result = get_table_for_year(year)
    result.to_csv("./output/table/table_{}.csv".format(year+1911), encoding='utf-8', index=False)


if __name__ == "__main__":
    main()
