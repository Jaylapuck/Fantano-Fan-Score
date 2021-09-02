from selenium import webdriver
import os
from selenium.webdriver.firefox.options import Options
import re
import pandas as pd

options = Options()
firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.binary_location = firefox_path
driver = webdriver.Firefox(options=options)

url = "https://www.youtube.com/watch?v=mmMrsCBFflE&list=PLP4CSgl7K7ori6-Iz-AWcX561iWCfapt_&index=8"

driver.get(url)

driver.find_element_by_xpath("//yt-formatted-string[@class='more-button style-scope ytd-video-secondary-info-renderer']").click()

footer = [i.text for i in driver.find_elements_by_xpath("//div[@id='description']//span[@class='style-scope "
                                                        "yt-formatted-string']")][-1] 

opinion_details = {}

for line in footer.split('\n'):
    for sub_str in ['FAV TRACKS']:
        if sub_str in line:
            opinion_details[sub_str] = line.split(':')[-1]



def extract_data(driver):

    # Read in Title
    title_string = driver.find_element_by_xpath(
        "//yt-formatted-string[@class='style-scope ytd-video-primary-info-renderer']").text
    clean_title = title_string.split(" ALBUM REVIEW")[0]

    # Read in Footer Description
    footer = [i.text for i in driver.find_elements_by_xpath(
        "//div[@id='description']//yt-formatted-string[@class='content style-scope ytd-video-secondary-info-renderer']")]

    # Extract Title Data
    clean_title = title_string.split(" ALBUM REVIEW")[0]
    title, artist = clean_title.split(' - ')

    # Populate Disctionary

    data_dict = {'Title': title,
    'Artist': artist,
    'Score': re.escape("\d+\/\d+", footer),
    'Fav Tracks': opinion_details.get('FAV TRACKS'),
    'Least Fav Tracks': opinion_details.get('LEAST FAV TRACK'),
    'Description': footer,
    }

    return data_dict


tmp = pd.DataFrame(columns=list(extract_data(driver).keys()))
for i in range(0, 3):
    tmp.loc[i] = extract_data(driver)