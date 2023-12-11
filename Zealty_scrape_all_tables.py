### PLEASE READ
### THIS SCRIPT REQUIRES A LOGIN FOR IT TO RUN SUCESSFULLY, HOWEVER, LOGIN AND PASSWORD INFORMATION WILL BE OMMITTED FOR SECURITY REASONS
### PLEASE MAKE AN ACCOUNT TO RUN THE CODE

### THIS FILE IS TO SCRAPE BC HOUSING INFORMATION FROM ZEALTY.CA
### THIS PROJECT IS FOR BCIT COMP 2452 ASSIGNMENT 2
### WRITTEN BY RAYEN FENG
### 2023-11-29

### IMPORT PACKAGES

import pickle
import time
import os
import re
from pathlib import Path

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
URL = "https://www.zealty.ca/search.html"

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

driver = webdriver.Chrome(service=Service(DRIVER_PATH))
driver.get(URL)
time.sleep(1)

### Entering Login information
login_button = driver.find_element(By.ID,'logButton')
login_button.click()
time.sleep(1)

email_login = '{ENTER EMAIL HERE}'
password_login = '{ENTER PASSWORD HERE}'

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

time.sleep(1)



### Selecting search button and clicking it

search_click = driver.find_element(By.XPATH,'//button[@onclick="gSmartSearchActive = true; doSearch(1, true);"]')
search_click.click()
time.sleep(1)

### list in table view for easier scraping
### switch to list view if not already in list view

list_view_button = driver.find_elements(By.XPATH,'//i[@title=" Show table list "]')
if len(list_view_button) == 1:
    list_view_button[0].click()
    time.sleep(1)

#### DEFINE FUNCTION TO SCRAPE TABLE FROM PAGE USING BS4

def scrape_house_table(page_source):
    ### Create soup
    soup = BeautifulSoup(page_source, 'html.parser')

    ### Find main table
    main_table = soup.find("div", {"id": "searchResults"})

    ### remove all unwanted rows
    unwanted_rows = main_table.find_all("tr", {"class": "noprint"})
    for row in unwanted_rows:
        row.extract()

    table_rows = main_table.find_all('tr')


    #print(len(unwanted_rows))
    #print(len(table_rows))

    ### LOOP THROUGH ROWS excluding header row

    all_table_rows = []

    for i in range(1,len(table_rows)):

        table_row_dict = {}
        tb_row = table_rows[i]


        td_tb_row = tb_row.find_all('td')
        #print(len(td_tb_row))


        ### MLS number
        MLS_number = td_tb_row[1].text
        table_row_dict['MLS'] = str(MLS_number)
        #print(MLS_number)

        ### address
        address_info = td_tb_row[2]
        address_name = address_info.find('div').text
        table_row_dict['address'] = str(address_name)
        #print(address_name)

        ### Property_info
        property_info = td_tb_row[3].find_all('div')
        for e in property_info:
            clean_prop = e.text.replace(' ', '')
            if clean_prop.isalnum() == True:
                table_row_dict['Property_info'] = str(clean_prop)
                #print(clean_prop)
                break

        ### size

        if td_tb_row[4].text.find('House Size') == 0:

            room_info = td_tb_row[4].find_all('div')[0].text
            size_info = td_tb_row[4].find_all('div')[1].text
            size_info = re.sub("[^0-9]", "", size_info)
            table_row_dict['area_sqft'] = int(size_info)

            bed_no = re.search(r'(\d+ bed)', room_info).group(1).replace('bed', '')
            bath_no = re.search(r'(\d+ bath)', room_info).group(1).replace('bath', '')
            table_row_dict['bed_num'] = int(bed_no)
            table_row_dict['bath_num'] = int(bath_no)

            #print(size_info)
        else:
            table_row_dict['area_sqft'] = np.nan
            table_row_dict['bed_num'] = np.nan
            table_row_dict['bath_num'] = np.nan


        ### price
        # price_info = td_tb_row[5].find('div', attrs={'style':'font-size: 14pt; font-weight: bold; color: green;'}).text
        price_info = td_tb_row[5].find('div', attrs={'style': re.compile(r'green;')}).text
        price_info = re.sub("[^0-9]", "", price_info)
        table_row_dict['asking_price'] = int(price_info)
        #print(price_info)


        ### Date
        ### store dates in tuple, order is price change, listing price or just make another column

        date_info = td_tb_row[6].find_all('div')

        if len(date_info) == 3:
            list_enter = date_info[0].text
            match = re.search(r'(\d+-\D+-\d+)', list_enter)
            list_date = match.group(1)
            list_date = pd.to_datetime(list_date)

            table_row_dict['price_change'] = np.nan
            table_row_dict['listing_entered'] = list_date
            #print(list_date)

        else:
            list_enter = date_info[0].text
            l_match = re.search(r'(\d+-\D+-\d+)', list_enter)
            list_date = l_match.group(1)
            list_date = pd.to_datetime(list_date)
            #print(list_date)

            pr_change_enter = date_info[3].text
            p_match = re.search(r'(\d+-\D+-\d+)', pr_change_enter)
            pr_change_date = p_match.group(1)
            pr_change_date = pd.to_datetime(pr_change_date)
            #print(pr_change_date)

            table_row_dict['price_change'] = pr_change_date
            table_row_dict['listing_entered'] = list_date


        ### agent info
        agent_info = td_tb_row[7].find('div').text
        def remove_rep_str(s):

            s_len_half = int(len(s)/2)
            half_str = s[0:s_len_half]
            repeat_num = s.find(half_str,1)
            if repeat_num != -1:
                return s[0:repeat_num]
            else:
                return s


        seller_info = remove_rep_str(agent_info)
        table_row_dict['seller_info'] = seller_info

        #print(seller_info)

        row_frame = pd.DataFrame.from_dict(table_row_dict, orient = 'index')
        all_table_rows.append(row_frame)


    ### format dataframe
    df3 = pd.concat(all_table_rows, ignore_index = True, axis = 1)
    df3 = df3.transpose()
    return (df3)



### LOOP THROUGH AND GATHER FUNCTION FROM ALL PAGES

all_house_listings_arr = []

for i in (range(0,29)):

    ## grab and scrape page source
    page_source = driver.page_source
    df_final = scrape_house_table(page_source)
    all_house_listings_arr.append(df_final)

    ## go to next page
    search_button_str = './/button[@onclick="doSearch(2, true);"][@style="width: 100px; visibility: visible;"]'
    rep_search_str = str('(' + str(2 + i) + ', true)')
    #print(rep_search_str)
    search_button_str = search_button_str.replace('(2, true)', rep_search_str)
    #print(search_button_str)
    #print('page' + str(1 + 20*i))

    #print(len(driver.find_elements(By.XPATH,search_button_str)))
    #print(len(driver.find_elements(By.XPATH,search_button_str)) == 0)

    ### if search button is not found (ie.invisible), break function
    if len(driver.find_elements(By.XPATH,search_button_str)) == 0:
        break

    next_page_button = driver.find_element(By.XPATH, search_button_str)
    next_page_button.click()
    time.sleep(2)

### store all information in dataframe
all_house_listings_df = pd.concat(all_house_listings_arr).reset_index()
print(all_house_listings_df)


### EXPORT FILE TO CSV
filepath = Path('C:/Python/Projects/ZealtyScrape/scrape_outputs/houses.csv')

filepath.parent.mkdir(parents=True, exist_ok=True)
all_house_listings_df.to_csv(filepath)



