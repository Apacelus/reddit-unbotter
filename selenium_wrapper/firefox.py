# Selenium for firefox
import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from json import load as json_load

if __name__ == "selenium_wrapper.firefox":
    with open('./config/settings.json', 'r') as file:
        settings_json = json_load(file)
    driver_options = webdriver.FirefoxOptions()
    driver_options.binary_location = settings_json["browser_path"]
    driver_options.add_argument("--incognito")
    driver = webdriver.Firefox(log_path="./logs/geckodriver.log",
                               service=FirefoxService(GeckoDriverManager().install()), options=driver_options)
    wait = WebDriverWait(driver, 10)


def get_session_cookie(username, password):
    driver.get("https://www.reddit.com/login/")
    driver.find_element(By.ID, 'loginUsername').send_keys(username)
    driver.find_element(By.ID, 'loginPassword').send_keys(password)
    sleep(1)
    driver.find_element(By.XPATH, '/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button').click()
    sleep(5)
    session_cookie = driver.get_cookie("reddit_session")["value"]
    logging.debug(driver.get_cookie("reddit_session"))
    driver.delete_all_cookies()
    return session_cookie


def login_account(session_cookie, username):
    logging.info("Logging in account: " + username)
    logging.debug("Session cookie: " + session_cookie)
    driver.get("https://www.reddit.com/")
    driver.add_cookie(
        {'name': 'reddit_session', 'value': session_cookie, 'path': '/', 'domain': 'reddit.com', 'secure': True,
         'httpOnly': True, 'sameSite': 'None'})
    driver.get("https://www.reddit.com/u/me")
    try:
        wait.until(ec.url_to_be('https://www.reddit.com/user/' + username + "/"))
    except TimeoutError:
        logging.warning("Couldnt login as user: " + username)
        return False


def scroll_to_next_post(post_num):
    driver.execute_script("return arguments[0].scrollIntoView();",
                          driver.find_element(By.XPATH,
                                              '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[5]/div['
                                              + str(post_num) + ']'))

# for testing:
# get_session_cookie("test_acc_3432", "zj2asdasdjfU$MuHHQ")
# login_account("2034960186510%2C2022-07-13T17%3A41%3A31%2Ca6c0ae783e770c9d52fd96d38ccab6d7e4b9881f", "test_acc_3432")
# driver.get("https://www.reddit.com/")
# scroll_to_next_post("3")
