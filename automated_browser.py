#!/usr/bin/python3
import json
import threading
import logging
from pynput import keyboard
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from win10toast import ToastNotifier

logging.basicConfig(level=logging.INFO)


class AutomatedBrowser:
    def __init__(self):
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)["automated_browser"]
        self.trigger_next_batch = True
        self.trigger_previous_site = False
        self.exit_program = False
        self.hotkeys = {
            'next_batch': keyboard.HotKey(
                keyboard.HotKey.parse(self.config["hotkeys"]["next_batch"]),
                self.on_activate_next_batch),
            'previous_site': keyboard.HotKey(
                keyboard.HotKey.parse(self.config["hotkeys"]["previous_site"]),
                self.on_activate_previous_site),
            'exit_program': keyboard.HotKey(
                keyboard.HotKey.parse(self.config["hotkeys"]["exit_program"]),
                self.on_activate_exit_program)
        }

    def on_activate_next_batch(self):
        logging.info("Next batch triggered")
        self.trigger_next_batch = True

    def on_activate_previous_site(self):
        logging.info("Previous site triggered")
        self.trigger_previous_site = True

    def on_activate_exit_program(self):
        logging.info("Exit program triggered")
        self.exit_program = True

    def start_listener(self):
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        return listener

    def on_press(self, key):
        for hotkey in self.hotkeys.values():
            hotkey.press(key)

    def on_release(self, key):
        for hotkey in self.hotkeys.values():
            hotkey.release(key)

    def get_options(self):
        options = Options()
        for key, value in self.config["browser_options"].items():
            options.set_preference(key, value)
        return options

    def login(self, browser):
        browser.get(self.config["login_site"])
        try:
            self.fill_form(browser, 'user_login', self.config["username"])
            if not self.config["password"]:
                return
            self.fill_form(
                browser, 'user_pass', self.config["password"], submit=True)
        except Exception as e:
            logging.error(f"Error while logging in: {e}")

    def fill_form(self, browser, field_id, value, submit=False):
        element = self.wait_for_element(browser, field_id, By.ID)
        if element is None:
            raise Exception(f"Could not find {field_id}")
        element.send_keys(value)
        if submit:
            element.submit()
        return element

    def wait_for_element(self, browser, element, by=By.TAG_NAME):
        try:
            return WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((by, element)))
        except Exception as e:
            logging.error(f"Error waiting for {element}: {e}")

    def get_starting_location(self, length):
        while True:
            try:
                location = int(input("Start: "))
                if 0 <= location < length:
                    return location
                logging.error("Invalid location. Try again.")
            except ValueError:
                logging.error("Input must be a number. Try again.")

    def move_to_next_site(self, location, sites):
        return location + 1 if location + 1 < len(sites) else -1

    def move_to_previous_site(self, location):
        return location - 1 if location - 1 >= 0 else -1

    def start_next_batch(self, location, sites, browser):
        location = self.move_to_next_site(location, sites)
        if location != -1:
            threading.Thread(target=self.open_batch, args=(browser, sites, location)).start()
        return location

    def start_previous_site(self, location, sites, browser):
        location = self.move_to_previous_site(location)
        if location != -1:
            threading.Thread(target=self.open_batch, args=(browser, sites, location)).start()
        return location

    def record_data(self, data):
        with open(self.config["output_file"], 'a') as file:
            str_data = ','.join(str(element) for element in data)
            file.write(str_data + '\n')

    def initialize_browser(self, browser):
        browser.set_window_position(-1000, 0) # Change first value to large pos/neg value for left/right monitor
        if self.config["maximize_browser"]: browser.maximize_window()

    def get_sites(self):
        with open(self.config["site_list"], 'r') as file:
            return file.read().splitlines()

    def open_batch(self, browser, sites, location):
        try:
            site = sites[abs(location)-2]
            logging.info(f"Opening pages for {site}")
            self.get_pages(browser, site)
        except IndexError:
            logging.error("Invalid site index")

    def get_pages(self, browser, site):
        self.close_other_tabs(browser)
        self.open_priority_pages(
            browser, site, self.config["pages"]["high_priority"])
        self.open_site_list(browser, site, self.config["pages"]["site_list"])
        browser.switch_to.window(browser.window_handles[self.config["displayed_page"]])
        self.notify_toast(f"{site} is ready.")

    def open_priority_pages(self, browser, site, pages):
        for url in pages:
            try:
                self.open_new_tab(browser, site, url)
                self.wait_for_element(browser, 'body')
            except Exception as e:
                logging.error(f"Error while opening priority page {url}: {e}")

    def open_site_list(self, browser, site, page):
        try:
            self.open_new_tab(browser, "trubox.ca", page[0] + site + page[1])
            element = self.wait_for_element(browser, 'table', By.TAG_NAME)
            rows = element.find_elements(By.CLASS_NAME, "blogname")
            for row in rows:
                link = row.find_element(By.TAG_NAME, "a")
                if link.text == site:
                    link.click()
        except Exception as e:
            logging.error(f"Error while opening site list page: {e}")

    def close_other_tabs(self, browser):
        for window_handle in browser.window_handles[1:]:
            browser.switch_to.window(window_handle)
            browser.close()
        browser.switch_to.window(browser.window_handles[-1])

    def open_new_tab(self, browser, site, url):
        browser.execute_script("window.open('');")
        browser.switch_to.window(browser.window_handles[-1])
        browser.get(f"https://{site}{url}")

    def notify_toast(self, message):
        if self.config["loaded_toast"]:
            toaster = ToastNotifier()
            toaster.show_toast("Pages Loaded", message,
                               duration=self.config["loaded_toast_duration"])

    def main(self):
        sites = self.get_sites()
        location = self.get_starting_location(len(sites))

        options = self.get_options()
        with webdriver.Firefox(options=options) as browser:
            self.initialize_browser(browser)
            self.login(browser)
            wpadminbar_element = self.wait_for_element(browser, 'wpadminbar', By.ID)
            if wpadminbar_element is None:
                logging.error("Could not find wpadminbar")
                return

            with self.start_listener() as listener:
                while not self.exit_program:
                    if self.trigger_next_batch:
                        location = self.start_next_batch(location, sites, browser)
                        self.trigger_next_batch = False

                    if self.trigger_previous_site:
                        location = self.start_previous_site(location, sites, browser)
                        self.trigger_previous_site = False

            logging.info("Exit program triggered, stopping execution.")


if __name__ == "__main__":
    AutomatedBrowser().main()
