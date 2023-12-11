#from Assignment2V2 import page_source
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import pickle

import os
import re

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

## Open saved text file for easier read
with open('/page_source.txt', 'rb') as f:
    page_source = pickle.load(f)

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


#df_final = scrape_house_table(page_source)
#print(df_final)


#### TESTING SECTION

# soup = BeautifulSoup(page_source, 'html.parser')
#
# ### Find main table
# main_table = soup.find("div", {"id": "searchResults"})
#
# ### remove all unwanted rows
# unwanted_rows = main_table.find_all("tr", {"class": "noprint"})
# for row in unwanted_rows:
#     row.extract()
#
# table_rows = main_table.find_all('tr')
# tb_row = table_rows[1]
# td_tb_row = tb_row.find_all('td')
#
# #price_info = td_tb_row[5].find('div', attrs={'style': 'font-size: 1.3rem; font-weight: bold; color: green;'}).text
#
# price_info = td_tb_row[5].find('div', attrs={'style': re.compile(r'green;')}).text
#
#
# print(price_info)
# # price_info = re.sub("[^0-9]", "", price_info)



