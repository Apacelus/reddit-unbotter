# Selenium for firefox
import json
import logging
import os

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

if __name__ == "selenium_drivers.firefox":
    # set env variables
    os.environ['WDM_LOG'] = str(logging.NOTSET)


def init_session(proxy_ip, proxy_port, socks_version):
    browser_options = webdriver.FirefoxOptions()
    with open('configs/settings.json', 'r') as file:
        settings_json = json.load(file)
    browser_options.binary_location = settings_json["browser_path"]

    # set firefox profile settings
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('network.proxy.type', 1)
    firefox_profile.set_preference('network.proxy.socks', proxy_ip)
    firefox_profile.set_preference('network.proxy.socks_port', proxy_port)
    firefox_profile.set_preference('network.proxy.socks_version', socks_version)

    session = webdriver.Firefox(
        service_log_path=f"/home/{os.getlogin()}/PycharmProjects/reddit-unbotter/logs/driver.log",
        service=FirefoxService(GeckoDriverManager(cache_valid_range=1).install()),
        options=browser_options, firefox_profile=firefox_profile)
    # session.minimize_window()
    return session
