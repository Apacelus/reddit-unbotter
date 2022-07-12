import account_wrapper
import logging
from ast import literal_eval
from random import randint
from time import sleep
from hashlib import md5
import json

user_agents_amount = 0


def retrieve_cookie(usernames):
    with open('data.json', 'r') as f:
        data_json = json.load(f)
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


def init_new_accounts():
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
    # adding new accounts:
    for string in to_be_added:
        temp_account_dict = {
            "password": string[string.find(":") + 1:],
            "user_agent": randint(0, user_agents_amount)
        }
        data_json[string[:string.find(":")]] = temp_account_dict
    with open('data.json', 'w') as f:
        json.dump(data_json, f)
    # retrieve login cookies for new accounts


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
        with open("user_agents.txt", "r") as f:
            global user_agents_amount
            user_agents_amount = len(f.readlines())
        logging.info("Available user agents: " + str(user_agents_amount))
        with open('settings.json', 'r') as json_file:
            settings_json = json.load(json_file)
        # Check whether the accounts file has changed
        with open("accounts.txt", 'r') as file_to_check:
            new_md5sum_of_accounts = md5(file_to_check.read().encode()).hexdigest()
            logging.info("New md5sum: " + new_md5sum_of_accounts)
            if not new_md5sum_of_accounts == settings_json["md5sum_of_accounts"]:
                logging.info("Found new accounts")
                settings_json["md5sum_of_accounts"] = new_md5sum_of_accounts
                with open('settings.json', 'w') as f:
                    json.dump(settings_json, f)
                init_new_accounts()


logging.basicConfig(filename='unbotter.log', level=logging.DEBUG,
                    format='%(asctime)s |%(levelname)s| %(message)s')
initialize()
