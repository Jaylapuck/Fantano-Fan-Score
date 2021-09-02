import re
import time

# Numpy Import
import numpy as np

# Panda Import
import pandas as pd

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options


def extract_data(driver):
    # Read in Title
    title_string = driver.find_element_by_xpath(
        "//yt-formatted-string[@class='style-scope ytd-video-primary-info-renderer']").text

    # Read in Footer Description
    full_description = "\n".join(
        [i.text for i in driver.find_elements_by_xpath(
            "//div[@id='description']//span[@class='style-scope yt-formatted-string']")
         if len(i.text) > 0]
    )

    # Extract Title Data
    title = ""
    artist = ""
    try:
        if title_string.find("ALBUM REVIEW") != -1:
            clean_title = title_string.split(" ALBUM REVIEW")[0]
            title, artist = clean_title.split('-')
        elif title_string.find("EP REVIEW") != -1:
            clean_title = title_string.split(" EP REVIEW")[0]
            title, artist = clean_title.split('-')
        elif title_string.find("MIX REVIEW") != -1:
            clean_title = title_string.split(" MIX REVIEW")[0]
            title, artist = clean_title.split('-')
        elif title_string.find("COMPILATION REVIEW") != -1:
            clean_title = title_string.split(" COMPILATION REVIEW")[0]
            title = clean_title
            print('could not find artist')
            artist = "not defined"
    except:
        title = "not defined"
        artist = "not defined"
        print('could not find the title and the artist')

    # Score Fetching
    try:
        score = re.findall("\d/\d+", full_description)[0]
    except:
        score = np.nan

    # Get Anthony's opinions'
    opinion_details = dict()
    for line in full_description.split('\n'):
        for sub_str in ['FAV TRACKS', 'LEAST FAV TRACK']:
            if sub_str in line:
                opinion_details[sub_str] = line.split(':')[-1]

    # Populate Disctionary
    data_dict = {'Title': title.strip(),
                 'Artist': artist.strip(),
                 'Score': score.strip(),
                 'Fav Tracks': opinion_details.get('FAV TRACKS'),
                 'Least Fav Tracks': opinion_details.get('LEAST FAV TRACK'),
                 'Description': full_description.strip(),
                 }
    print(data_dict)
    return data_dict


def completion_check(driver):
    # Keeps a record of the current video on the view
    current_video_string = 0
    last_video_string = 0
    playlist_location_string = driver.find_element_by_xpath(
        "//yt-formatted-string[@class='index-message style-scope ytd-playlist-panel-renderer']").text

    try:
        playlist_location_string_regex = re.findall("\d+ / \d+", playlist_location_string)[0]
        current_video_string = int(playlist_location_string_regex.split(' / ')[0])
        last_video_string = int(playlist_location_string_regex.split(' / ')[1])
    except:
        print('ERROR IN completion_check ')

    return current_video_string == last_video_string


def go_next_video(driver):
    try:
        driver.find_element_by_xpath(
            "//a[@class='ytp-next-button ytp-button']").click()
    except:
        print('Cannot continue to next video')


video_db = pd.DataFrame(columns=['ID', 'Title', 'Artist', 'Score', 'Fav Tracks', 'Least Fav Tracks', 'Description'])

if __name__ == '__main__':

    options = Options()
    firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    options.binary_location = firefox_path
    driver = webdriver.Firefox(options=options)
    url = "https://www.youtube.com/watch?v=k-37V-1igRw&list=PLP4CSgl7K7ormX2pL9h0inES2Ub630NoL&index=135"
    driver.get(url)
    # driver.maximize_window()

    data_list = list()
    volume_button = driver.find_element_by_xpath("//button[@class='ytp-mute-button ytp-button']").click()

    while not completion_check(driver):
        threshold = 4
        try:

            # element_present = EC.presence_of_element_located((By.ID, 'description'))
            # WebDriverWait(driver, threshold).until(element_present)
            time.sleep(threshold)

            # Expands the more button in the description
            more_button = driver.find_element_by_xpath("//yt-formatted-string[@class='more-button style-scope "
                                                       "ytd-video-secondary-info-renderer']").click()

            # Pause the video
            #pause_button = driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button ytp-play-button-playlist']").click()

            ActionChains(driver).move_to_element(more_button).perform()

        except:
            print(f'Exceeded time threshold {threshold}')

        # expand description

        # Keeps a record of the current video on the view
        # go to next video
        data_list.append(extract_data(driver))
        go_next_video(driver)
