from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By

from utils.computation import time_to_filename
from utils.converter import move_files

def get_map(url_map, delay_1 = 6, resource = "../resources/maps"):
    print("Getting map")
    driver = webdriver.Chrome()
    driver.get(url_map)
    sleep(delay_1)
    driver.save_screenshot("Map_tmp.png")
    driver.quit()
    move_files("Map_tmp.png", resource)

def get_print_screens(url, url_map, do_screenshot = True, delay_1 = 6, delay_2 = 1, screenshot_number = 10, screenshot_time = 10.0, resource = "../recources/raw_pictures_3"):
    if do_screenshot:
        print("Chromium init")
        driver = webdriver.Chrome()
        print("Navigate to website")
        driver.get(url)
        sleep(delay_1)
        element = driver.find_element(By.CLASS_NAME, 'play-pause')
        element.click()
        sleep(delay_2)
        for i in range(screenshot_number):
            sleep((screenshot_time - delay_2) / screenshot_number)
            name = time_to_filename(60 - (i * 60) // screenshot_number)
            print(f"Screenshot {i}: {name}")
            driver.save_screenshot(time_to_filename(60 - (i * 60) // screenshot_number))
            move_files(name, resource)
        print("Quiting")
        driver.quit()
        print("The end")
        get_map(url_map, delay_1=delay_1)
    else:
        print("Screenshot omitted!")