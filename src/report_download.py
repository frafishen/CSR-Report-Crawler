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
import pandas as pd
import urllib.request
from time import sleep
from pdf2image import convert_from_path
from tqdm import tqdm
import ssl
import random

ssl._create_default_https_context = ssl._create_unverified_context
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
]

# Constants
CONFIG_FILE_PATH = './config.yaml'
CONFIG = {}
TIMESTAMP_DIR, TABLE_PATH, ROOT_PATH, PDF_DIR, JPG_DIR = '', '', '', '', ''
company_name_path = ""

def load_config(TIMESTAMP_DIR):
    """Load configurations from the config file."""
    # Determine the directory of the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to config.yaml
    config_path = os.path.join(script_dir, CONFIG_FILE_PATH)

    global CONFIG, TABLE_PATH, COMPANY_NAME, PDF_DIR, JPG_DIR, company_name_path
    with open(config_path, 'r') as file:
        CONFIG = yaml.safe_load(file)
    
    ROOT_PATH = TIMESTAMP_DIR
    TABLE_PATH = os.path.join(ROOT_PATH, CONFIG['COMPANY']['TABLE_PATH'])
    COMPANY_NAME = os.path.join(script_dir, CONFIG['COMPANY']['NAME_PATH'])
    PDF_DIR = os.path.join(ROOT_PATH, CONFIG['SAVE']['PDF_DIR'])
    JPG_DIR = os.path.join(ROOT_PATH, CONFIG['SAVE']['IMG_DIR'])

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

def download_file_with_retry(url, file_name, retries=3):
    user_agent = random.choice(USER_AGENTS)
    headers = {"User-Agent": user_agent}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
                out_file.write(response.read())
            break
        except urllib.error.URLError as e:
            wait_time = 10 * (attempt + 1)
            print(f"Error encountered. Retrying in {wait_time} seconds...")
            sleep(wait_time)
        except Exception as e:
            raise e
    sleep(random.uniform(10, 20))

def download_files(data, download_path, year, flag):
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
    for pdf_file in glob.glob(os.path.join(pdf_dir, "*.pdf")):
        images_from_path = convert_from_path(pdf_file, output_folder=jpg_save_dir, last_page=1, first_page=0)
        base_filename = os.path.splitext(os.path.basename(pdf_file))[0] + '.jpg'
        for page in images_from_path:
            page.save(os.path.join(jpg_save_dir, base_filename), 'JPEG')
        for ppm_file in glob.glob(os.path.join(jpg_save_dir, "*.ppm")):
            os.remove(ppm_file)

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

def run(year, flag, TIMESTAMP_DIR):
    load_config(TIMESTAMP_DIR)

    if flag == 2:
        convert_pdf_to_jpg(PDF_DIR, JPG_DIR)
    
    else:
        companyData_path = f"{TABLE_PATH}table_{year}.csv"

        data, company_name = read_data(companyData_path, company_name_path)
        data = match_and_modify_data(data, company_name)
        data_copy = data.copy()
        data_copy['統一編號'] = data_copy['統一編號'].str.extract('(\d+)')
        data_copy.to_csv(companyData_path, encoding='utf-8', index=False)
        download_files(data, PDF_DIR, year, flag)
        if flag == 0:
            convert_pdf_to_jpg(PDF_DIR, JPG_DIR)

