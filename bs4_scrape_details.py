import pickle
import time
import os
import re
from pathlib import Path
import requests

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

# DRIVER_PATH = "C:/Python/Chromedriver/chromedriver.exe"
#
# URL = 'https://www.zealty.ca/mls-R2836837/402-20061-FRASER-HIGHWAY-Langley-BC/'
# MLS_id = str(re.search(r'(mls-R\d+)', URL).group(1).replace('mls-', ''))
# driver = webdriver.Chrome(service=Service(DRIVER_PATH))
# driver.get(URL)
#
# time.sleep(2)
# page_source = driver.page_source
#
# # DUMP TO TXT FILE
#
# with open('C:/Python/Projects/ZealtyScrape/scrape_outputs/page_source_details2.txt','wb') as f:
#     pickle.dump(page_source, f)
#
#
# with open('C:/Python/BCIT/Week2/ZealtyScrape/scrape_outputs/page_source_details2.txt', 'rb') as f:
#     page_source = pickle.load(f)


### create a function that accepts link and returns the page scraped
def scrape_property_details(URL):

    ### SET DRIVER SEE IF YOU CAN REMOVE THIS LATER OR COMMENT IT OUT

    DRIVER_PATH = "C:/Python/Chromedriver/chromedriver.exe"
    driver = webdriver.Chrome(service=Service(DRIVER_PATH))
    driver.get(URL)

    time.sleep(2)
    page_source = driver.page_source

    ### CREATE SOUP
    soup = BeautifulSoup(page_source, 'html.parser')


    ### get MLS

    MLS_id = str(re.search(r'(mls-R\d+)',URL).group(1).replace('mls-', ''))

    ### scrape description

    desc_section = soup.find("div", {"id": "details-section"})

    if desc_section is not None:
        desc_text = desc_section.findNext("div", {"style": re.compile(r'font')}).text
        #print(desc_text)
    else:
        desc_text = None


    ### scrape sections
    ### make a fucntion to return the parent of section

    all_sections = soup.find_all("div", {"class": "section-heading"})
    def return_table_match(all_sections, table_title_q):

        for section in all_sections:
            section_title = section.findChild(string=True)
            if section_title == table_title_q:
                return section.parent


    ### scrape property details
    property_section = return_table_match(all_sections, 'Property Details')
    #print(property_section)
    if property_section is not None:

        prop_details_table = property_section.find("table", {"class": "stripedTable"})
        prop_details_rows = prop_details_table.find_all('tr')

        property_details_dict = {}

        for row in prop_details_rows:

            row_data = row.find_all('td')

            prop_title_col = row_data[0]
            prop_val_col = row_data[1]

            if prop_title_col.findChild('div') == None:
                #print(prop_title_col.find(string=True))
                #print(prop_val_col.find(string=True))
                property_details_dict[str(prop_title_col.find(string=True)).strip()] = prop_val_col.find(string=True)

            else:
                # print(prop_title_col.find(string=True))
                # print(prop_val_col.find(string=True))
                property_details_dict[str(prop_title_col.find(string=True)).strip()] = prop_val_col.find(string=True)
                #print(prop_val_col.findChildren())
                # print((prop_title_col.findChildren(string=True)))
                # print((prop_val_col.findChildren(string = True)))
                #for i in range(len())

                for title,info in zip(prop_title_col.findChildren(string = True),prop_val_col.findChildren(string = True)):
                    property_details_dict[str(title).strip()] = str(info)
                    # print(title.text, info.text)


        property_ser = pd.Series(property_details_dict).str.strip()
        #print(property_ser)
    else:
        property_ser = None


    ### scrape features

    features_section = return_table_match(all_sections, 'Features & Amenities')
    if features_section is not None:
        features_list = []
        for f in features_section.find_all('li'):
            features_list.append(f.text.strip())

        #print(features_list)
    else:
        features_list = None

    ## scrape property assessment

    assessment_section = soup.find('div', {'id': 'assessmentInfo'})

    if assessment_section is not None:

        assessment_rows = assessment_section.find_all('tr')
        assessment_row_headers = assessment_rows[0].find_all('th')
        header_row = []

        for header in assessment_row_headers:
            # print(item.text)
            header_row.append(header.text)

        row_data = []

        for row in assessment_rows[1:]:
            all_items = row.find_all('td')
            #print(all_items)
            row_array = []
            for item in all_items:
                #print(item.text)
                row_array.append(item.text)

            row_data.append(row_array)

        assessment_df = pd.DataFrame.from_records(row_data, columns=header_row )
        #print(assessment_df)
    else:
        assessment_df = None


    ## finding assessment ratio

    a_ratio_find = soup.find(string = re.compile(r'Asking Price to Assessed Value ratio'))
    if assessment_section is not None:
        found_ratio = (a_ratio_find.parent.text)
        assessment_ratio = re.search(r'(\d+)', found_ratio).group(1)
        #print(assessment_ratio)
    else:
        assessment_ratio = None



    ## MAKE A CLASS ITEM

    class Property:
      def __init__(self, mls, property_details, features, property_assessment, assessment_ratio,desc_text):
        self.mls = mls
        self.property_details = property_details
        self.features = features
        self.property_assessment = property_assessment
        self.assessment_ratio = assessment_ratio
        self.desc_text = desc_text


    property_item = Property(MLS_id, property_ser,features_list, assessment_df, assessment_ratio, desc_text)

    return property_item

# link = 'https://www.zealty.ca/mls-R2833514/26440-29-AVENUE-Langley-BC/'
# property_item = scrape_property_details(link)
#
# print(property_item.mls)
# print(property_item.property_details)
# print(property_item.features)
# print(property_item.property_assessment)
# print(property_item.assessment_ratio)
# print(property_item.desc_text)
