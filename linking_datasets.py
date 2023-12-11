
### import files

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

### LOAD DRIVER INFORMATION AND START WEBSITE

DRIVER_PATH = "C:/Python/Chromedriver/chromedriver.exe"
# URL = "https://www.zealty.ca/search.html"

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

driver = webdriver.Chrome(service=Service(DRIVER_PATH))
# driver.get(URL)
# time.sleep(1)

df = pd.read_csv('/houses.csv')
df = df.drop(columns= ['Unnamed: 0', 'index'])

#print(df.head(5))

### FIX RUNTIMER ERRORS
from bs4_scrape_details import scrape_property_details

### CREATE A LIST OF PROPERTIES
property_links = []
property_item_arr = []

df_testing = df.iloc[0:5]
print(df_testing)

for index, row in df_testing.iterrows():
    MLS_num = row['MLS'].strip().replace('#', '')
    adress_string = row['address'].strip().replace(' ', '-')
    geo_region = "Langley"
    house_link = f'https://www.zealty.ca/mls-{MLS_num}/{adress_string}-{geo_region}-BC/'
    #print(house_link)
    property_links.append(house_link)

    ### also run scrape function
    print(house_link)
    house_class_item = scrape_property_details(house_link)
    property_item_arr.append(house_class_item)




df_testing['property_links'] = property_links
df_testing['house_details'] = property_item_arr
print(df_testing)

