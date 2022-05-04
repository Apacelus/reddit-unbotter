import account_wrapper
import logging
from ast import literal_eval
from random import randint
from time import sleep

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


def initialize():
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


logging.basicConfig(filename='unbotter.log', level=logging.DEBUG,
                    format='%(asctime)s |%(levelname)s| %(message)s')
initialize()
login_users()
