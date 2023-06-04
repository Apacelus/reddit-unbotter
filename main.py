import atexit
import configparser
import json
import logging
import os
import termios
import tty
from itertools import zip_longest

import calendar_json
from functions import *


class KeyGetter:
    def arm(self):
        self.old_term = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)

        atexit.register(self.disarm)

    def disarm(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_term)

    def getch(self):
        self.arm()
        ch = sys.stdin.read(1)[0]
        self.disarm()
        return ch


def ia_selection(question: str, options: list = None, flags: list = None) -> str:
    print_question(question)
    return _draw_ia_selection(options, flags)


def _draw_ia_selection(options: list, flags: list = None):
    __UNPOINTED = " "
    __POINTED = ">"
    __INDEX = 0
    __LENGTH = len(options)
    __ARROWS = __UP, _ = 65, 66
    __ENTER = 10

    if flags is None:
        flags = []

    def _choices_print():
        for i, (option, flag) in enumerate(zip_longest(options, flags, fillvalue='')):
            if i == __INDEX:
                print(f" {__POINTED} {{0}}{option} {flag}{{1}}".format('\033[94m', '\033[0m'))
            else:
                print(f" {__UNPOINTED} {option} {flag}")

    def _choices_clear():
        print(f"\033[{__LENGTH}A\033[J", end='')

    def _move_pointer(ch_ord: int):
        nonlocal __INDEX
        __INDEX = max(0, __INDEX - 1) if ch_ord == __UP else min(__INDEX + 1, __LENGTH - 1)

    def _main_loop():
        kg = KeyGetter()
        _choices_print()
        while True:
            key = ord(kg.getch())
            if key in __ARROWS:
                _move_pointer(key)
            _choices_clear()
            _choices_print()
            if key == __ENTER:
                _choices_clear()
                _choices_print()
                break

    _main_loop()
    return options[__INDEX]


def init_logger():
    # Print output to console and log to file

    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Create a file handler to log to a file
    file_handler = logging.FileHandler("logs/unbotter.log")
    file_handler.setLevel(logging.INFO)
    # Create a stream handler to log to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    # Create a formatter to specify the log message format
    formatter = logging.Formatter("%(asctime)s |%(levelname)s| %(message)s")
    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def get_user_input(prompt, default_value, min_value, max_value):
    while True:
        try:
            user_input = input(
                "\033[92m" + f"{prompt} ({min_value}-{max_value}), default: {default_value}: " + "\033[0m")
            if user_input == "":
                user_input = default_value
                print("\n")  # avoid logging.info() to be on the same line as the input
                logging.info(f"{default_value} selected")
                return default_value
            else:
                user_input = int(user_input)
        except ValueError:
            print_warning(f"Invalid {prompt.lower()}")
            continue
        if user_input < min_value or user_input > max_value:
            print_warning(f"Invalid {prompt.lower()}, try again")
            continue
        logging.info(f"{user_input} selected")
        return user_input


def add_new_accounts(config: configparser.ConfigParser) -> None:
    logging.info("Adding the following accounts: " + ", ".join(config.options("NewAccounts")))
    # Check if each new account has a password
    if accounts_with_no_password := [
        account
        for account in config["NewAccounts"]
        if config.get("NewAccounts", account).strip() in ["", None]
    ]:
        logging.critical(f"The following new accounts have no password: {accounts_with_no_password}")
        exit(1)

    user_answer = input(
        "\033[92m" + "Would you like to use individual settings for the new accounts? (Y/n): " + "\033[0m")
    # if user_answer == "Y" or user_answer == "y" or user_answer == "yes" or user_answer == "":
    print_warning("Individual settings not yet implemented, using settings for all new accounts")
    print("Hint: Press enter for default value")

    activity_level = get_user_input("Activity level", 3, 0, 5)
    vote_chance = get_user_input("Vote chance", 40, 0, 100)
    upvote_ratio = get_user_input("Upvote ratio", 90, 0, 100)
    comment_chance = get_user_input("Comment chance", 40, 0, 100)

    # load proxy list
    with open("configs/proxy.json", "r") as file:
        proxy_json = json.load(file)
    # load data.json
    with open("configs/data.json", "r") as file:
        data_json = json.load(file)

    # add new accounts
    proxy_counter = 0
    for account in config["NewAccounts"]:
        logging.info(f"Adding {account}to data.json")
        # add account to data.json
        # get session cookie
        session_cookie = browser_wrapper.get_session_cookie(account, config.get("NewAccounts", account).strip(),
                                                            proxy_json[proxy_counter]["host"],
                                                            proxy_json[proxy_counter]["port"],
                                                            proxy_json[proxy_counter]["socksVersion"])
        if session_cookie == "Incorrect username or password":
            logging.error(f"Couldn't login {account}, skipping")
            continue

        temp_account_dict = {
            "password": config.get("NewAccounts", account).strip(),
            "session_cookie": session_cookie,
            "activity_level": activity_level,
            "vote_chance": vote_chance,
            "upvote_ratio": upvote_ratio,
            "comment_chance": comment_chance,
            "proxy_ip": proxy_json[proxy_counter]["host"],
            "proxy_port": proxy_json[proxy_counter]["port"],
            "socks_version": proxy_json[proxy_counter]["socksVersion"],
        }
        data_json[account] = temp_account_dict
    with open("configs/data.json", "w") as file:
        json.dump(data_json, file)

    # remove new accounts from accounts.conf, but keep the section + add accounts to InitializedAccounts + add accounts to calendar
    for account in config["NewAccounts"]:
        config.remove_option("NewAccounts", account)
        calendar_json.initialize_account(account)
        config.set("InitializedAccounts", account)


def remove_accounts(config: configparser.ConfigParser) -> None:
    logging.info("Removing the following accounts: " + ", ".join(config.options("ToBeRemovedAccounts")))
    # load data.json
    with open("configs/data.json", "r") as file:
        data_json = json.load(file)
    # remove accounts from data.json
    for account in config["ToBeRemovedAccounts"]:
        data_json.pop(account)
    with open("configs/data.json", "w") as file:
        json.dump(data_json, file)

    # remove accounts from accounts.conf, but keep the sections + remove accounts from calendar
    for account in config["ToBeRemovedAccounts"]:
        config.remove_option("ToBeRemovedAccounts", account)
        config.remove_option("InitializedAccounts", account)
        calendar_json.remove_account(account)

    logging.info("Accounts removal complete")


def parse_accounts_conf():
    logging.info("Parsing accounts.conf")
    # read accounts.conf
    config = configparser.ConfigParser()
    config.read("configs/accounts.conf")

    # Check if accounts.conf is empty
    if not config.sections():
        logging.critical("accounts.conf is empty, creating new")
        cpfile("default_configs/accounts.conf", "configs/accounts.conf")
        exit(1)

    # Check if accounts need to be removed
    if config.options("ToBeRemovedAccounts"):
        remove_accounts(config)

    # Check if new accounts have been added
    if config.options("NewAccounts"):
        add_new_accounts(config)


def check_jsons():
    # Check if json files exist and create them if needed
    for file in ["data.json", "calendar.json", "settings.json"]:
        try:
            with open(f"configs/{file}", "r") as json_test:
                json.load(json_test)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logging.error(f"{file} is missing or corrupted, creating new")
            cpfile(f"default_configs/{file}", f"configs/{file}")

    # Check if proxy.json exists
    if not path_exists("configs/proxy.json"):
        logging.info("Attempting to downloading proxy list")
        download_file("https://proxy.koddit.com/home/getproxydata",
                      "configs/proxy.json")
        with open("configs/proxy.json", "r") as file:
            proxy_json = json.load(file)
        # json has useless data key, remove it
        proxy_json = proxy_json["data"]
        with open("configs/proxy.json", "w") as file:
            json.dump(proxy_json, file)


def check_browser_path():
    with open('configs/settings.json', 'r') as file:
        settings_json = json.load(file)
    if not path_exists(settings_json["browser_path"]):
        logging.warning("Browser not found")
        logging.info("Searching system for browsers")
        browser_paths_win = {
            "msedge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe"
        }
        browser_paths_linux = {
            "msedge": r"/usr/bin/microsoft-edge",
            "chrome": r"/usr/bin/google-chrome",
            # TODO: Add more chromium paths

            "firefox": r"/usr/bin/firefox",
            "firefox_snap": r"/snap/bin/firefox",
            "firefox_flatpak_home": f"/home/{os.getlogin()}/.local/share/flatpak/app/org.mozilla.firefox/current/"
                                    f"active/files/lib/firefox/firefox",
            "firefox_flatpak": "/var/lib/flatpak/app/org.mozilla.firefox/current/active/files/lib/firefox/firefox",

            "librewolf_flatpak_home": f"/home/{os.getlogin()}/.local/share/flatpak/app/io.gitlab.librewolf-community"
                                      f"/current/active/files/lib/librewolf/librewolf",
            "librewolf_flatpak": "/var/lib/flatpak/app/io.gitlab.librewolf-community/current/active/files/lib/librewolf/librewolf"
        }
        available_browsers = {}
        match sys.platform:
            case "linux":
                for browser_path in browser_paths_linux:
                    if path_exists(browser_paths_linux[browser_path]):
                        logging.info(f"Found {browser_path}")
                        available_browsers[browser_path] = browser_paths_linux[
                            browser_path
                        ]
            case "win32":  # win64 will report itself as win32
                for browser_path in browser_paths_win:
                    if path_exists(browser_paths_win[browser_path]):
                        logging.info(f"Found {browser_path}")
                        available_browsers[browser_path] = browser_paths_win[
                            browser_path
                        ]
            case _:
                logging.critical(f"{sys.platform} not supported")
                exit(1)

        user_selection = ia_selection("Please select a browser", options=available_browsers.keys())
        logging.info(f"User selected the {user_selection} browser")
        # TODO: Add support for multiple browsers

        settings_json["browser_path"] = available_browsers[user_selection]
        settings_json["browser"] = user_selection
        with open('configs/settings.json', 'w') as file:
            json.dump(settings_json, file)


if __name__ == "__main__":
    # Create dirs if needed
    mkdir("logs")
    mkdir("configs")
    init_logger()
    logging.info("Created log and config directories if needed")
    check_jsons()
    check_browser_path()

    import browser_wrapper

    # Parse accounts.conf
    parse_accounts_conf()

    # start main loop
    #wrapper.main()
