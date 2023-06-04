import json
import logging
from random import randint, uniform
from time import sleep

from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

base_xpath = "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[5]/div["


def init_browser(proxy_ip, proxy_port, socks_version):
    return driver.init_session(proxy_ip, proxy_port, socks_version)


def get_session_cookie(username, password, proxy_ip, proxy_port, socks_version):
    browser = init_browser(proxy_ip, proxy_port, socks_version)
    browser.get("https://www.reddit.com/login/")
    browser.find_element(By.ID, 'loginUsername').send_keys(username)
    browser.find_element(By.ID, 'loginPassword').send_keys(password)
    sleep(1)
    browser.find_element(By.XPATH, '/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button').click()
    sleep(5)
    session_cookie = browser.get_cookie("reddit_session")["value"]
    logging.debug(browser.get_cookie("reddit_session"))
    browser.quit()
    return session_cookie


def prepare_session(session_cookie: str, username: str) -> str:
    with open('./config/data.json', 'r') as data_file:
        data_json = json.load(data_file)
    browser = init_browser(data_json[username]["proxy_ip"], data_json[username]["proxy_port"],
                           data_json[username]["socks_version"])
    logging.info(f"Preparing session for account: {username}")
    logging.debug(f"Session cookie: {session_cookie}")
    browser.get("https://www.reddit.com/")
    browser.add_cookie(
        {'name': 'reddit_session', 'value': session_cookie, 'path': '/', 'domain': 'reddit.com', 'secure': True,
         'httpOnly': True, 'sameSite': 'None'})
    # cookie denial cookie, to get rid of cookie prompt
    browser.add_cookie(
        {'name': 'eu_cookie', 'value': "{%22opted%22:true%2C%22nonessential%22:false}", 'path': '/',
         'domain': 'reddit.com', 'secure': False,
         'httpOnly': False, 'sameSite': 'None'})
    browser.get("https://www.reddit.com/u/me")
    try:
        WebDriverWait(browser, 10).until(ec.url_to_be(f"https://www.reddit.com/user/{username}/"))
        browser.get("https://www.reddit.com/")
        delete_top_bar(browser)
    except TimeoutError:
        logging.error(f"Couldn't login as user: {username}")
        browser.quit()
        return "Couldn't login"
    # removing reddit popup
    # try:
    #     browser.find_element(By.XPATH,
    #                          "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[1]/button").click()
    #     logging.info("Removed reddit suggestion")
    # except NoSuchElementException:
    #     pass


def delete_top_bar(browser):
    try:
        browser.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, browser.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/header"))
        logging.debug("Deleted top bar!!!")
    except NoSuchElementException:
        logging.warning("Couldn't find top bar")


def join_subreddit(subreddit_id):
    pass


# vote true = up, vote false = down
def vote_post(browser, post_id, vote):
    pass


def leave_comment(browser, comment_text):
    pass


def scroll_to_next_post(browser, post_id):
    browser.execute_script("return arguments[0].scrollIntoView();",
                          browser.find_element(By.XPATH, base_xpath + str(post_id) + ']'))
    try:
        if "promotedlink" not in browser.find_element(
            By.XPATH, base_xpath + str(post_id) + "]/div/div"
        ).get_attribute("class"):
            return post_id
        logging.info("Found ad post, skipping")
        post_id += 1
        return scroll_to_next_post(post_id, browser)
    except NoSuchElementException:
        logging.warning("Found broken post")
        post_id += 1
        return scroll_to_next_post(post_id, browser)


def upvote_post(browser, post_id):
    try:
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[1]").click()
    except ElementClickInterceptedException:
        delete_top_bar(browser)
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[1]").click()
    except NoSuchElementException:
        logging.warning("Couldnt find downvote button, trying alternate path")
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div/div/div[2]/div/button[1]").click()


def downvote_post(browser, post_id):
    try:
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[2]").click()
    except ElementClickInterceptedException:
        delete_top_bar(browser)
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[2]/div/button[2]").click()
    except NoSuchElementException:
        logging.warning("Couldnt find downvote button, trying alternate path")
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div/div/div[2]/div/button[2]").click()


def enter_comments(browser, post_id):
    try:
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div[3]/div[5]/div[2]/a").click()
    except NoSuchElementException:
        logging.warning("Couldnt find comment button, trying alternate path")
        browser.find_element(By.XPATH, base_xpath + str(post_id) + "]/div/div/div/div/div[3]/div[5]/div[2]/a").click()


def scroll_comments(browser, amount):
    counter = 1
    try:
        while counter <= amount:
            print(
                f'/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[5]/div/div/div/div[{counter}]'
            )
            browser.execute_script(
                "return arguments[0].scrollIntoView();",
                browser.find_element(
                    By.XPATH,
                    f'/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[5]/div/div/div/div[{counter}]',
                ),
            )
            counter += randint(1, 3)
            sleep(uniform(2, 4))
    except NoSuchElementException:
        logging.info("Couldnt find next comment, using alt path")
        try:
            while counter <= amount:
                print(
                    '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[6]/div/div/div/div[' + str(
                        counter) + ']')
                browser.execute_script("return arguments[0].scrollIntoView();", browser.find_element(By.XPATH,
                                                                                                   '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[6]/div/div/div/div[' + str(
                                                                                                       counter) + ']'))
                sleep(uniform(2, 4))
                counter += randint(1, 3)
        except NoSuchElementException:
            logging.info("Couldnt find next comment, probably no more comments")
            browser.execute_script("window.history.go(-1)")
            sleep(2)
            return counter


def write_comment(browser, comment_text):
    WebDriverWait(browser, 10).until(ec.element_to_be_clickable(
        (By.XPATH,
         "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div/div"))).send_keys(
        comment_text)
    browser.find_element(By.XPATH,
                        "/html/body/div[1]/div/div[2]/div[3]/div/div/div/div[2]/div[1]/div[3]/div[3]/div[2]/div/div/div[3]/div[1]/button").click()


# the main loop
def main():
    logging.info("Starting main loop")
    # load data.json
    with open('configs/data.json', 'r') as file:
        data = json.load(file)
    # for testing:
    prepare_session(data["anonym_opinion_1"]["session_cookie"], "anonym_opinion_1")
    # i = 1
    # while i < 10:
    #     print("At start: " + str(i))
    #     print("before scroll: " + str(i))
    #     i = scroll_to_next_post(i)
    #     print("after scroll: " + str(i))
    #     sleep(uniform(3, 7))
    #     if random.randint(0, 1) == 0:
    #         upvote_post(i)
    #     else:
    #         downvote_post(i)
    #     i += 1
    #     sleep(uniform(0.5, 2))
    #     print("At end: " + str(i))

    # post_id = 1
    # post_id = selenium_wrapper.scroll_to_next_post(post_id)
    # selenium_wrapper.enter_comments(post_id)
    # selenium_wrapper.write_comment("lol")

    # sleep(2)
    # print(scroll_comments(10))
    # post_id += 3
    # post_id = scroll_to_next_post(post_id)
    # enter_comments(post_id)
    # sleep(2)
    # print(scroll_comments(10))


if __name__ == "browser_wrapper":
    logging.basicConfig(filename='./logs/unbotter.log', level=logging.INFO,
                        format='%(asctime)s |%(levelname)s| %(message)s')
    logging.info("\n\nNew log:")
    logging.info("Initializing")

    with open('configs/settings.json', 'r') as file:
        settings_json = json.load(file)

    match settings_json["browser"]:
        case "firefox" | "firefox_snap" | "librewolf_home" | "librewolf_var":
            logging.info("Using geckodriver")
            import selenium_drivers.firefox as driver
        case "chrome":
            logging.info("Using generic ChromeDriver")
            import selenium_drivers.chromium as driver
        case "msedge":
            logging.info("Using Microsoft Edge Driver")
            import selenium_drivers.msedge as driver
        case _:
            logging.error("Browser not found")
            exit(1)
