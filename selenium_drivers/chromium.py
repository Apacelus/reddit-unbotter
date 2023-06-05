# Selenium for chromium based browsers
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def init_session(proxy_ip, proxy_port, socks_version):
    chrome_options = webdriver.ChromeOptions()
    with open("user_configs/settings.json", "r") as file:
        settings_json = json.load(file)
    chrome_options.binary_location = settings_json["browser_path"]
    # chrome_options.add_argument(f'--proxy-server=socks{socks_version}://{proxy_ip}:{proxy_port}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # hide webdriver.navigator flag
    session = webdriver.Chrome(
        service_log_path=f"/home/{os.getlogin()}/PycharmProjects/reddit-unbotter/logs/driver.log",
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options)
    # session.minimize_window()
    return session
