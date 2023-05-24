#!/usr/bin/python3

# Reading the config file
import json

# Custom key combinations
from pynput import keyboard

# Desktop notifications
from win10toast import ToastNotifier

# Automated web browser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Background operations
import threading

# Global Variables
TRIGGER_NEXT_BATCH = False
COMBINATIONS = None
CURRENT_KEYS = set()
CONFIG = None

# Configuration Loading
with open('config.json', 'r') as config_file:
    CONFIG = json.load(config_file)


def on_activate():
    print("Triggered")
    global TRIGGER_NEXT_BATCH
    TRIGGER_NEXT_BATCH = True

def start_listener():
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse(CONFIG["hotkey"]),
        on_activate)
    with keyboard.Listener(
            on_press=hotkey.press,
            on_release=hotkey.release) as l:
        l.join()

# Selenium and Toast Functions


def get_options():
    options = Options()
    for key, value in CONFIG["browser_options"].items():
        options.set_preference(key, value)
    return options


def get_pages(browser, site):
    close_other_tabs(browser)
    open_priority_pages(browser, site, CONFIG["pages"]["highPriority"])
    #open_low_priority_pages(browser, site, CONFIG["pages"]["lowPriority"])
    notify_toast(f"{site} is ready.")


def open_priority_pages(browser, site, pages):
    for url in pages:
        try:
            open_new_tab(browser, site, url)
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body')))
        except Exception as e:
            print(f"Error while opening priority page {url}: {e}")

def open_low_priority_pages(browser, site, pages):
    for url in pages:
        try:
            open_new_tab(browser, site, url)
        except Exception as e:
            print(f"Error while opening priority page {url}: {e}")


def close_other_tabs(browser):
    for window_handle in browser.window_handles[1:]:
        browser.switch_to.window(window_handle)
        browser.close()
    browser.switch_to.window(browser.window_handles[-1])


def open_new_tab(browser, site, url):
    browser.execute_script("window.open('');")
    browser.switch_to.window(browser.window_handles[-1])
    browser.get(f"https://{site}{url}")


def notify_toast(message):
    toaster = ToastNotifier()
    toaster.show_toast("Pages Loaded", message,
                       duration=CONFIG["loaded_toast_duration"])


def login(browser):
    browser.get(CONFIG["login_site"])
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'user_login')))
    username_element = browser.find_element(By.ID, 'user_login')
    username_element.send_keys(CONFIG["username"])

    if CONFIG["password"] != "":
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'user_pass')))
            password_element = browser.find_element(By.ID, 'user_pass')
            password_element.send_keys(CONFIG["password"])
            password_element.submit()
        except Exception as e:
            print(f"Error while entering password: {e}")

# location Handling


def get_starting_location(length):
    while True:
        try:
            location = int(input("Start: "))
            if 0 <= location < length:
                return location
            print("Invalid location. Try again.")
        except ValueError:
            print("Input must be a number. Try again.")


def update_location(location, sites):
    location = location - 1 if CONFIG["reverse_list"] else location + 1
    if location >= len(sites) + CONFIG["list_offset"] or location <= CONFIG["list_offset"]:
        return -1
    return location

# Main Program Functions


def main():
    sites = get_sites()
    list_offset = CONFIG["list_offset"]
    location = get_starting_location(len(sites))

    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()

    browser = open_browser()
    login(browser)
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'dashboard-widgets')))

    open_batch(browser, sites, location, list_offset)

    global TRIGGER_NEXT_BATCH
    while location != -1:
        if TRIGGER_NEXT_BATCH:
            # Start a new thread to load the pages
            threading.Thread(target=open_batch, args=(
                browser, sites, location, list_offset)).start()
            TRIGGER_NEXT_BATCH = False
            location = update_location(location, sites)
    browser.quit()


def get_sites():
    with open(CONFIG["site_list"], 'r') as file:
        return file.read().splitlines()


def open_browser():
    return webdriver.Firefox(options=get_options())


def open_batch(browser, sites, location, list_offset):
    print(f"Opening pages for {sites[abs(location)-2]}")
    get_pages(browser, sites[location-list_offset])


# Execution
if __name__ == "__main__":
    main()
