import configparser
import json
import logging

import calendar_json
from functions import *


def get_user_input(prompt, default_value, min_value, max_value):
    while True:
        try:
            user_input = input(f"{prompt} ({min_value}-{max_value}), default: {default_value}: ")
            if user_input == "":
                user_input = default_value
                return user_input
            else:
                user_input = int(user_input)
        except ValueError:
            logging.error(f"Invalid {prompt.lower()}")
            print(f"Invalid {prompt.lower()}, try again")
            continue
        if user_input < min_value or user_input > max_value:
            logging.error(f"Invalid {prompt.lower()}")
            print(f"Invalid {prompt.lower()}, try again")
            continue
        return user_input


def add_new_accounts(config: configparser.ConfigParser) -> None:
    logging.info("Adding the following accounts: " + ", ".join(config.options("NewAccounts")))
    # Check if each new account has a password
    if accounts_with_no_password := [
        account
        for account in config["NewAccounts"]
        if config.get("Accounts", account).strip() in ["", None]
    ]:
        logging.error(f"The following new accounts have no password: {accounts_with_no_password}")
        print_error(f"The following new accounts have no password: {accounts_with_no_password}")
        exit(1)

    print_question("Would you like to use individual settings for the new accounts?")
    user_answer = input("Y/n: ")
    # if user_answer == "Y" or user_answer == "y" or user_answer == "yes" or user_answer == "":
    print_warning("Individual settings not yet implemented, using settings for all new accounts")
    print("Hint: Press enter for default value")

    activity_level = get_user_input("Activity level", 3, 0, 5)
    vote_chance = get_user_input("Vote chance", 40, 0, 100)
    upvote_ratio = get_user_input("Upvote ratio", 90, 0, 100)
    comment_chance = get_user_input("Comment chance", 40, 0, 100)

    # load proxy list
    with open("config/proxy.json", "r") as file:
        proxy_json = json.load(file)
    # load data.json
    with open("config/data.json", "r") as file:
        data_json = json.load(file)

    # add new accounts
    proxy_counter = 0
    for account in config["NewAccounts"]:
        # add account to data.json
        temp_account_dict = {
            "password": config.get("NewAccounts", account).strip(),
            "session_cookie": wrapper.get_session_cookie(account, config.get("NewAccounts", account).strip(),
                                                         proxy_json[proxy_counter]),
            "activity_level": activity_level,
            "vote_chance": vote_chance,
            "upvote_ratio": upvote_ratio,
            "comment_chance": comment_chance,
            "proxy_ip": proxy_json[proxy_counter]
        }
        data_json[account] = temp_account_dict
    with open("config/data.json", "w") as file:
        json.dump(data_json, file)

    # remove new accounts from accounts.conf, but keep the section + add accounts to InitializedAccounts + add accounts to calendar
    for account in config["NewAccounts"]:
        config.remove_option("NewAccounts", account)
        calendar_json.initialize_account(account)
        config.set("InitializedAccounts", account)


def remove_accounts(config: configparser.ConfigParser) -> None:
    logging.info("Removing the following accounts: " + ", ".join(config.options("ToBeRemovedAccounts")))
    # load data.json
    with open("config/data.json", "r") as file:
        data_json = json.load(file)
    # remove accounts from data.json
    for account in config["ToBeRemovedAccounts"]:
        data_json.pop(account)
    with open("config/data.json", "w") as file:
        json.dump(data_json, file)

    # remove accounts from calendar.json
    with open("config/calendar.json", "r") as file:
        calendar_json = json.load(file)
    for account in config["ToBeRemovedAccounts"]:
        calendar_json.pop(account)
    with open("config/calendar.json", "w") as file:
        json.dump(calendar_json, file)

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
        logging.warning("accounts.conf is empty, creating new")
        cpfile("default_configs/accounts.conf", "configs/accounts.conf")
        print("accounts.conf is empty, please fill it with accounts")
        exit(1)

    # Check if accounts need to be removed
    if config.options("ToBeRemovedAccounts"):
        remove_accounts(config)

    # Check if new accounts have been added
    if config.options("NewAccounts"):
        add_new_accounts(config)


if __name__ == "__main__":
    # Create dirs if needed
    mkdir("logs")
    mkdir("config")
    # start logging system
    logging.basicConfig(filename="logs/unbotter.log", level=logging.INFO,
                        format="%(asctime)s |%(levelname)s| %(message)s")
    logging.info("Created log and config directories if needed")

    # Check if data.json exists
    try:
        with open("configs/data.json", "r") as data:
            settings_json = json.load(data)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logging.info("data.json not found, creating new")
        cpfile("default_configs/data.json", "configs/data.json")

    # Check if proxy.json exists
    if not path_exists("config/proxy.json"):
        logging.info("Attempting to downloading proxy list")
        download_file("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json",
                      "config/proxy.json")

    # Check if calendar.json exists
    try:
        with open("configs/calendar.json", "r") as data:
            settings_json = json.load(data)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logging.info("calendar.json not found, creating new")
        cpfile("default_configs/calendar.json", "configs/calendar.json")

    # Parse accounts.conf
    parse_accounts_conf()

    # start main loop
    wrapper.main()
