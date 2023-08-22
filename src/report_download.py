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

# Constants
CONFIG_FILE_PATH = './config.yaml'
CONFIG = None
TABLE_PATH = None
COMPANY_NAME = None
PDF_DIR = None
JPG_DIR = None

def load_config():
    """Load configuration from the YAML file."""
    global CONFIG, TABLE_PATH, COMPANY_NAME, PDF_DIR, JPG_DIR
    with open(CONFIG_FILE_PATH, 'r') as file:
        CONFIG = yaml.safe_load(file)
    TABLE_PATH = CONFIG['COMPANY']['TABLE_PATH']
    COMPANY_NAME = CONFIG['COMPANY']['NAME_PATH']
    PDF_DIR = CONFIG['SAVE']['PDF_DIR']
    JPG_DIR = CONFIG['SAVE']['IMG_DIR']

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

def download_files(data, download_path, year, flag):
    if flag == 1:
         for i in tqdm(range(len(data["CSR報告超連結"])), desc="Downloading reports"):
            url = data["CSR報告超連結"].iloc[i]
            file_name = os.path.join(download_path, str(year) + str(data["統一編號"].iloc[i]) + ".pdf")
            urllib.request.urlretrieve(url, file_name)
            sleep(3)

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


if __name__ == "__main__":
    main()

def run(year, flag):
    load_config()

    companyData_path = f"{TABLE_PATH}table_{year}.csv"

    data, company_name = read_data(companyData_path, COMPANY_NAME)
    data = match_and_modify_data(data, company_name)
    download_files(data, PDF_DIR, year, flag)
    convert_pdf_to_jpg(PDF_DIR, JPG_DIR)

    

