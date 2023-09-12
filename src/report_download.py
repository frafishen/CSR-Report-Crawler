"""
Report Download Script
----------------------
This script contains functions to download reports and convert them to images.
Created on Fri. Aug. 22, 2023
@author: Jie-Yu Shen
"""

import os
import sys
import glob
import yaml
import re
import pandas as pd
import urllib.request
from time import sleep
from pdf2image import convert_from_path
from tqdm import tqdm
import ssl
import random
import http.client

ssl._create_default_https_context = ssl._create_unverified_context
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
]

# Constants
CONFIG_FILE_PATH = './config.yaml'
CONFIG = {}
TIMESTAMP_DIR, TABLE_PATH, ROOT_PATH, PDF_DIR, JPG_DIR, cat_entry = '', '', '', '', '', ''
company_name_path = ""

def load_config(prefix_path):
    """Load configurations from the config file."""
    # Determine the directory of the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to config.yaml
    config_path = os.path.join(script_dir, CONFIG_FILE_PATH)

    global CONFIG, TABLE_PATH, COMPANY_NAME, PDF_DIR, JPG_DIR, ROOT_PATH, company_name_path
    with open(config_path, 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    TABLE_PATH = os.path.join(prefix_path, CONFIG['COMPANY']['TABLE_PATH'])
    COMPANY_NAME = os.path.join(script_dir, CONFIG['COMPANY']['NAME_PATH'])
    PDF_DIR = os.path.join(prefix_path, CONFIG['SAVE']['PDF_DIR'])
    JPG_DIR = os.path.join(prefix_path, CONFIG['SAVE']['IMG_DIR'])
    ROOT_PATH = os.path.join(script_dir, CONFIG['SAVE']['ROOT_DIR'])

    company_name_path = os.path.join(script_dir, COMPANY_NAME)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def read_data(company_data_path, company_name_path):
    """Read and preprocess company data and company names from given paths."""
    data = pd.read_csv(company_data_path, encoding='utf-8', header=None)
    data = data.drop(0)
    new_header = data.iloc[0]
    data = data[1:]
    data.columns = new_header
    company_name = pd.read_csv(company_name_path, encoding='utf-8')
    return data, company_name

def match_and_modify_data(data, company_name):
    """Match and modify data using company names."""
    for i in range(len(data["公司代號"])):
        for j in range(len(company_name["公司代號"])):
            if str(data["公司代號"].iloc[i]) == company_name["公司代號"].iloc[j]:
                data["公司完整名稱"].iloc[i] = company_name["公司名稱"].iloc[j]
                data["統一編號"].iloc[i] = company_name["_統一編號"].iloc[j]
                break
 
    data['統一編號'] = data['統一編號'].str.replace('\t', '')
    return data

def get_latest_directory(cat_entry):
    """
    Get the latest directory for a given category based on the naming format "YYMMDD_HHMM_{cat}".
    """
    pattern = os.path.join(ROOT_PATH, f"*_{cat_entry}")
    directories = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if len(directories) >= 2:
        return directories[0], directories[1]
    if directories:
        return directories[0], None
    else:
        return None, None

def get_latest_two_tables(cat_entry, year):
    """
    Get the paths of the latest two tables of the specified category and year.
    """
    # Construct the pattern of the tables based on the given category and year
    base_directory = get_latest_directory(cat_entry)
    print(f"近兩期{cat_entry}公司下載項目")
    print(base_directory)
    if base_directory[1]:
        lat_path = os.path.join(base_directory[0], f"table/table_{year}.csv")
        pre_path = os.path.join(base_directory[1], f"table/table_{year}.csv")
        return lat_path,  pre_path
    elif base_directory[0]:
        path = os.path.join(base_directory[0], f"table/table_{year}.csv")
        return path, None        
    else:
        return None, None
    
def get_new_companies(cat_entry, year):
    """Compare the latest table with the previous version and return a list of new or updated companies."""
    latest_table_path, previous_table_path = get_latest_two_tables(cat_entry, year)
    # print(latest_table_path, previous_table_path)
    if not previous_table_path:
        latest_table = pd.read_csv(latest_table_path)
        return latest_table["公司完整名稱"].tolist()
    latest_table = pd.read_csv(latest_table_path)
    previous_table = pd.read_csv(previous_table_path)
    new_companies = set(latest_table["公司完整名稱"]) - set(previous_table["公司完整名稱"])
    return list(new_companies)


def download_file_with_retry(url, file_name, retries=3):
    user_agent = random.choice(USER_AGENTS)
    headers = {"User-Agent": user_agent}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
                out_file.write(response.read())
            break
        except (urllib.error.URLError, http.client.RemoteDisconnected) as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Error encountered. Retrying in {wait_time} seconds...")
            sleep(wait_time)
        except Exception as e:
            print(f"Attempt {attempt + 1} of {retries} failed with error: {e}. Retrying in {wait_time} seconds...")
            raise e
    sleep(random.uniform(10, 20))

def download_files(data, download_path, year, flag, new_company_list):
    data = data[data['公司完整名稱'].isin(new_company_list)]  # Filter data based on company_list
    print("待下載之更新公司名單")
    print(data['公司完整名稱'])
    if len(data) == 0:
        print("No new companies to download.")
        return
    if flag == 1:
        for i in tqdm(range(len(data["CSR報告超連結"])), desc="Downloading reports"):
            url = data["CSR報告超連結"].iloc[i]
            file_name = os.path.join(download_path, str(year) + str(data["統一編號"].iloc[i]) + ".pdf")
            
            try:
                download_file_with_retry(url, file_name)
            except Exception as e:
                print(f"Failed to download {url} due to {e}")

    else:
        for i in range(0,1):
            url = data["CSR報告超連結"].iloc[i]
            file_name = os.path.join(download_path, str(year) + str(data["統一編號"].iloc[i]) + ".pdf")
            urllib.request.urlretrieve(url, file_name)
            sleep(3)

def convert_pdf_to_jpg(pdf_dir, jpg_save_dir):
    for pdf_file in tqdm(glob.glob(os.path.join(pdf_dir, "*.pdf")), desc = "Download Covers"):
        images_from_path = convert_from_path(pdf_file, output_folder=jpg_save_dir, last_page=1, first_page=0)
        base_filename = os.path.splitext(os.path.basename(pdf_file))[0] + '.jpg'
        for page in images_from_path:
            page.save(os.path.join(jpg_save_dir, base_filename), 'JPEG')
        for ppm_file in glob.glob(os.path.join(jpg_save_dir, "*.ppm")):
            os.remove(ppm_file)

def extract_numbers_from_filenames(folder_path):
    # List all files in the given directory
    files = os.listdir(folder_path)
    
    # Define a regex pattern to extract number from the filename
    pattern = re.compile(r'\d{4}_(\d+)')
    
    # Extract numbers and store in a list with underscore prefix
    numbers = []
    for filename in files:
        match = pattern.match(filename)
        if match:
            numbers.append("_" + match.group(1))
    
    return numbers

def recheck(data, PDF_DIR):
    # Check whether the downloaded files are corrupted or not by checking their md5sum values and delete them when they're corrupted
    print('rechecking...')
    existed_report_numbers = extract_numbers_from_filenames(PDF_DIR)
    expected_report_numbers = data["統一編號"]

    redownload_list = []
    for report_number in expected_report_numbers:
        if report_number not in existed_report_numbers:
            redownload_list.append(report_number)

    print(len(redownload_list))
        
    return redownload_list

def run_recheck(year, recheck_folder):
    recheck_pdf_path = f"../output/{recheck_folder}/pdf"
    recheck_table_path = f"../output/{recheck_folder}/table/table_{year}.csv"

    data = pd.read_csv(recheck_table_path, encoding='utf-8', header=0)
    for i in range(5):
        redownload_number_list = recheck(data, recheck_pdf_path)
        redownload_company_list = data[data["統一編號"].isin(redownload_number_list)]["公司完整名稱"]
        download_files(data, recheck_pdf_path, year, 1, redownload_company_list)


def main():
    """Main function to orchestrate report downloading and processing."""
    companyData_path = "../table_2022.csv"
    companyName_path = resource_path('../bin/company_name_number.csv')

    year = "2022"
    download_path = "output"
    pdf_dir = "../output/pdf/"
    jpg_save_dir = "../output/jpg"

    data, company_name = read_data(companyData_path, companyName_path)
    data = match_and_modify_data(data, company_name)
    download_files(data, download_path, year)
    convert_pdf_to_jpg(pdf_dir, jpg_save_dir)

if __name__ == "__main__":
    main()

def run(year, flag, cat_entry, prefix_path):
    load_config(prefix_path)

    if flag == 2:
        convert_pdf_to_jpg(PDF_DIR, JPG_DIR)
    
    else:
        companyData_path_csv = f"{TABLE_PATH}table_{year}.csv"
        companyData_path_excel = f"{TABLE_PATH}table_{year}.xlsx"

        data, company_name = read_data(companyData_path_csv, company_name_path)
        data = match_and_modify_data(data, company_name)
        data_copy = data.copy()
        data_copy.to_csv(companyData_path_csv, encoding='utf-8', index=False)
        data_copy.to_excel(companyData_path_excel, index=False)
        new_company_list = get_new_companies(cat_entry, year)
        download_files(data, PDF_DIR, year, flag, new_company_list)
        
        # Check whether the downloaded files are corrupted or not by checking their md5sum values and delete them when they're corrupted
        for i in range(5):
            redownload_list = recheck(data, PDF_DIR)
            download_files(data, PDF_DIR, year, flag, redownload_list)

        convert_pdf_to_jpg(PDF_DIR, JPG_DIR)
