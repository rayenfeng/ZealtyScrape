import pickle
import time

import time
import os
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pathlib import Path

### set pandas viewing options
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

### LOAD DRIVER INFORMATION AND START WEBSITE

DRIVER_PATH = "C:/Python/Chromedriver/chromedriver.exe"
URL = "https://www.zealty.ca/search.html"

driver = webdriver.Chrome(service=Service(DRIVER_PATH))
driver.get(URL)
time.sleep(2)

### Entering Login information
login_button = driver.find_element(By.ID,'logButton')
login_button.click()
time.sleep(1)

email_login = 'rayen.fpss@gmail.com'
password_login = '!1Gppdell'

driver.find_element(By.NAME,'email').send_keys(email_login)
driver.find_element(By.NAME,'password').send_keys(password_login)

time.sleep(1)

### find and click login button
login_click = driver.find_element(By.XPATH,'//button[@onclick="userLogin();"]')
login_click.click()

time.sleep(1)


### Select Geographic region from dropdown

select = Select(driver.find_element(By.ID,'database'))
select.select_by_visible_text('Langley')
time.sleep(1)


### Selecting property type

to_check = ['HSE', 'APT', 'TWN']

prop_type_menu = driver.find_element(By.XPATH, '//div[@class="type-menu-value-button"]')
prop_type_menu.click()

all_type_checkboxes = driver.find_elements(By.XPATH,'//div[@id="type-menu-panel"]//input[@type="checkbox"]')

to_check_list = []
for t in to_check:
    type_box = driver.find_element(By.XPATH,'//input[@type="checkbox"][@value="%s"]'%(t))
    to_check_list.append(type_box)

uncheck_list = [i for i in all_type_checkboxes if i not in to_check_list]

for checkbox in to_check_list:
    if checkbox.is_selected() == False:
        checkbox.click()

for checkbox in uncheck_list:
    if checkbox.is_selected() == True:
        checkbox.click()

driver.find_element(By.XPATH,'//div[@class="type-menu-action-section"]//button[@class="type-menu-action-button"]').click()

time.sleep(1)

### changing min and max price

min_price_dropdown = Select(driver.find_element(By.NAME,'minprice'))
min_price_dropdown.select_by_value('1000')

max_price_dropdown = Select(driver.find_element(By.NAME,'maxprice'))
max_price_dropdown.select_by_value('3000')

time.sleep(4)

### Selecting search button and clicking it

search_click = driver.find_element(By.XPATH,'//button[@onclick="gSmartSearchActive = true; doSearch(1, true);"]')
search_click.click()
time.sleep(2)

### list in table view for easier scraping
### switch to list view if not already in list view

list_view_button = driver.find_elements(By.XPATH,'//i[@title=" Show table list "]')
if len(list_view_button) == 1:
    list_view_button[0].click()
    time.sleep(4)

# saves page source to BS$
## https://medium.com/ymedialabs-innovation/web-scraping-using-beautiful-soup-and-selenium-for-dynamic-page-2f8ad15efe25


page_source = driver.page_source


## DUMP TO TXT FILE
# with open('C:/Python/BCIT/Week2/page_source.txt','wb') as f:
#     pickle.dump(page_source, f)


## NAVIGATE TO NEXT PAGE


