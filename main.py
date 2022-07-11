import account_wrapper
import logging
from ast import literal_eval
from random import randint
from time import sleep
from hashlib import md5
import json

user_agents_amount = 0


def login_users(mode="force"):
    match mode:
        case "force":  # will override all cookies
            with open('accounts.txt', 'r') as f:
                raw_accounts = f.readlines()
            with open('user_agents.txt', 'r') as f:
                user_agent_raw = f.readlines()
            for line in raw_accounts:
                username = line[:line.find(':')]
                password = line[line.find(':') + 1:]
                logging.info("Attempting to login " + username + ":" + password)
                user_agent = user_agent_raw[randint(0, user_agents_amount)]
                session_cookie = account_wrapper.get_session_cookie(username, password, user_agent)
                if not isinstance(session_cookie, str):
                    print("Login failed, check credentials: " + username + "," + password)
                    logging.error("Login failed, check credentials: " + username + "," + password)
                    return "Wrong credentials"
                else:
                    logging.info("Login successful: " + username + "," + password)
                    user_data = {'user_agent': user_agent, 'session_cookie': session_cookie}
                    with open('stored_data.txt', 'r') as f:
                        old_file = literal_eval(f.read())
                    old_file[username] = user_data
                    with open('stored_data.txt', 'w') as f:
                        f.write(str(old_file))
                # sleep(randint(60, 600))
        case "preserve":
            # will not overwrite existing session-cookies
            pass


def initialize_old():
    logging.info("\n\nNew log:")
    logging.info("Initializing")
    try:
        with open('stored_data.txt', 'r') as f:
            f.read()
    except FileNotFoundError:
        logging.info("Config not found")
        with open('stored_data.txt', 'w') as f:
            f.write('{}')
    global user_agents_amount
    with open('user_agents.txt', 'r') as f:
        user_agents_amount = len(f.readlines()) - 1
    logging.info("Available user agents: " + str(user_agents_amount))


def add_accounts():
    logging.info("Comparing accounts")
    # read accounts.txt and parse it
    with open("accounts.txt", "r") as f:
        accounts_file = f.readlines()
        del accounts_file[0]
        del accounts_file[0]
        for x in range(len(accounts_file)):
            try:
                accounts_file.remove("")
            except ValueError:
                pass
            accounts_file[x] = accounts_file[x].replace("\n", "")
    with open('data.json', 'r') as f:
        data_json = json.load(f)
    # check if username and passwd match and exist
    to_be_added = []
    for x in range(len(accounts_file)):
        try:
            if not data_json[accounts_file[x][:accounts_file[x].find(":")]]["password"] == accounts_file[x][
                                                                                           accounts_file[x].find(
                                                                                               ":") + 1:]:
                to_be_added.append(accounts_file[x])
        except KeyError:
            to_be_added.append(accounts_file[x])
    logging.info("accounts to be added: " + str(to_be_added))


def initialize():
    logging.info("\n\nNew log:")
    logging.info("Initializing")
    with open("accounts.txt", "r") as f:
        accounts_amount = len(f.readline()) - 2
    if accounts_amount <= 0:
        logging.error("No accounts found, exiting")
        print('No accounts found! Please fill in at least one account in "accounts.txt"')
        exit(1)
    else:
        # Read the settings.json file
        with open('settings.json', 'r') as json_file:
            settings_json = json.load(json_file)
        # Check whether the accounts file has changed
        with open("accounts.txt", 'rb') as file_to_check:
            md5sum_of_accounts = md5(file_to_check.read()).hexdigest()
            logging.info("Current md5sum: " + md5sum_of_accounts)
            if not md5sum_of_accounts == settings_json["md5sum_of_accounts"]:
                logging.info("Found new accounts")
                add_accounts()


logging.basicConfig(filename='unbotter.log', level=logging.DEBUG,
                    format='%(asctime)s |%(levelname)s| %(message)s')
initialize()
