import logging
import os
from hashlib import md5
from json import load as jload
from json import dump as jdump
from os import path, mkdir
from random import randint, uniform


def init_new_accounts():
    logging.info("Comparing accounts")
    # read accounts.txt and parse it
    with open("./config/accounts.txt", "r") as f:
        accounts_file = f.readlines()
        del accounts_file[0]
        del accounts_file[0]
        for x in range(len(accounts_file)):
            try:
                accounts_file.remove("")
            except ValueError:
                pass
            accounts_file[x] = accounts_file[x].replace("\n", "")
    with open('./config/data.json', 'r') as f:
        data_json = jload(f)
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
    print("New accounts found. Would you like to use individual settings for the accounts?")
    user_answer = input("Y/Enter or N")
    # if user_answer == "Y" or user_answer == "y" or user_answer == "yes" or user_answer == "":
    print("Individual settings not yet implemented, using settings for all new accounts")
    print("Hint: Press enter for default value")
    while True:
        try:
            activity_level = input("Activity level(0-5), default: 3\n")
            if activity_level == "":
                activity_level = 3
                break
            else:
                activity_level = int(activity_level)
        except ValueError:
            logging.error("Invalid activity level")
            print("Invalid activity level, try again")
            continue
        if activity_level < 0 or activity_level > 5:
            logging.error("Invalid activity level")
            print("Invalid activity level, try again")
            continue
        else:
            break
    while True:
        try:
            vote_chance = input("Vote chance(0-100), default: 40\n")
            if vote_chance == "":
                vote_chance = 40
                break
            else:
                vote_chance = int(vote_chance)
        except ValueError:
            logging.error("Invalid vote chance")
            print("Invalid vote chance, try again")
            continue
        if vote_chance < 0 or vote_chance > 100:
            logging.error("Invalid vote chance")
            print("Invalid vote chance, try again")
            continue
        else:
            break
    while True:
        try:
            upvote_ratio = input("Upvote ratio(0-100), default: 90\n")
            if upvote_ratio == "":
                upvote_ratio = 90
                break
            else:
                upvote_ratio = int(upvote_ratio)
        except ValueError:
            logging.error("Invalid upvote ratio")
            print("Invalid upvote ratio, try again")
            continue
        if upvote_ratio < 0 or upvote_ratio > 100:
            logging.error("Invalid upvote ratio")
            print("Invalid upvote ratio, try again")
            continue
        else:
            break
    while True:
        try:
            comment_chance = input("Comment chance(0-100), default: 40\n")
            if comment_chance == "":
                comment_chance = 40
                break
            else:
                comment_chance = int(comment_chance)
        except ValueError:
            logging.error("Invalid comment chance")
            print("Invalid comment chance, try again")
            continue
        if comment_chance < 0 or comment_chance > 100:
            logging.error("Invalid comment chance")
            print("Invalid comment chance, try again")
            continue
        else:
            break
    # adding new accounts:
    import wrapper
    #######################################################
    # RANDOMIZATION/TOR ROUTING NEEDED HERE!!!!!!!!!!!!!  #
    #######################################################
    with open('./config/proxy.json', 'r') as f:
        proxy_json = jload(f)
    proxy_counter = 0
    for string in to_be_added:
        match activity_level:
            case 0:
                active_days = [randint(0, 27)]
                activation_times = [str(randint(0, 24)) + ":" + str(randint(0, 59))]
                online_duration = 1
            case 1:
                active_days = [randint(0, 6), randint(13, 20)]
                activation_times = [str(randint(0, 24)) + ":" + str(randint(0, 59))]
                online_duration = 2
            case 2:
                active_days = [randint(0, 2), randint(3, 5), randint(6, 8), randint(9, 11), randint(12, 14),
                               randint(15, 17), randint(18, 20), randint(21, 23), randint(24, 27)]
                activation_times = [str(randint(0, 24)) + ":" + str(randint(0, 59))]
                online_duration = 0.5
            case 3:
                active_days = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                               24, 25, 26, 27]
                activation_times = [str(randint(0, 24)) + ":" + str(randint(0, 59))]
                online_duration = 1
            case 4:
                active_days = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                               24, 25, 26, 27]
                activation_times = [str(randint(0, 10)) + ":" + str(randint(0, 59)),
                                    str(randint(14, 24)) + ":" + str(randint(0, 59))]
                online_duration = 1
            case 5:
                active_days = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                               24, 25, 26, 27]
                activation_times = [str(randint(0, 10)) + ":" + str(randint(0, 59)),
                                    str(randint(14, 24)) + ":" + str(randint(0, 59))]
                online_duration = 2
        temp_account_dict = {
            "password": string[string.find(":") + 1:],
            "session_cookie": wrapper.get_session_cookie(string[:string.find(":")], string[string.find(":") + 1:],
                                                         proxy_json[proxy_counter]),
            "active_days": active_days,
            "activation_times": activation_times,
            "online_duration": online_duration,
            "vote_chance": vote_chance,
            "upvote_ratio": upvote_ratio,
            "comment_chance": comment_chance,
            "proxy_ip": proxy_json[proxy_counter]
        }
        data_json[string[:string.find(":")]] = temp_account_dict
        with open('./config/data.json', 'w') as file:
            jdump(data_json, file)


if __name__ == "__main__":
    if not path.isdir("./logs"):
        logging.info("Creating log directory")
        mkdir("./logs")
    logging.basicConfig(filename='./logs/unbotter.log', level=logging.INFO,
                        format='%(asctime)s |%(levelname)s| %(message)s')
    if not path.isdir("./config"):
        logging.info("Creating config directory")
        mkdir("./config")
    try:
        with open('./config/data.json', 'r') as file:
            settings_json = jload(file)
    except FileNotFoundError:
        logging.info("data.json not found, creating new")
        print("data.json not found, restoring default")
        with open('./config/data.json', 'w') as file:
            with open("./default_config/data.json", "r") as template:
                file.write(template.read())
    try:
        with open("./config/accounts.txt", "r") as f:
            accounts_amount = len(f.readlines()) - 2
    except FileNotFoundError:
        logging.info("accounts.txt not found, creating new")
        print("accounts.txt not found, restoring default")
        with open('./config/accounts.txt', 'w') as file:
            with open("./default_config/accounts.txt", "r") as template:
                file.write(template.read())
        with open("./config/accounts.txt", "r") as file:
            accounts_amount = len(file.readlines()) - 2
    logging.debug("accounts_amount: " + str(accounts_amount))
    if accounts_amount <= 0:
        logging.info("No accounts found, exiting")
        print('No accounts found! Please fill in at least one account in "/config/accounts.txt"')
        exit(1)
    else:
        # Read the settings.json file
        try:
            with open('./config/settings.json', 'r') as file:
                settings_json = jload(file)
        except FileNotFoundError:
            logging.info("settings.json not found, creating new")
            print("settings.json not found, restoring default")
            with open('./config/settings.json', 'w') as file:
                with open("./default_config/settings.json", "r") as template:
                    file.write(template.read())
            with open('./config/settings.json', 'r') as file:
                settings_json = jload(file)
        # Check whether the accounts file has changed
        with open("./config/accounts.txt", 'r') as file_to_check:
            new_md5sum_of_accounts = md5(file_to_check.read().encode()).hexdigest()
            logging.info("New md5sum: " + new_md5sum_of_accounts)
            if not new_md5sum_of_accounts == settings_json["md5sum_of_accounts"]:
                logging.info("Found new accounts")
                settings_json["md5sum_of_accounts"] = new_md5sum_of_accounts
                with open('./config/settings.json', 'w') as f:
                    jdump(settings_json, f)
                init_new_accounts()
            else:
                logging.info("No new accounts found")
    import wrapper

    # starting main loop
    wrapper.main()
