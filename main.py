import account_wrapper
import logging
from ast import literal_eval

user_agents_amount = 0


def get_user_agent(user_agent_id):
    with open('user_agents.txt', 'r') as f:
        user_agent = f.readlines()[user_agent_id]
    return user_agent


def login_user(username, password, user_agent):
    session_cookie = account_wrapper.get_session_cookie(username, password, user_agent)
    if not isinstance(session_cookie, str):
        print("Login failed, check credentials: " + username + "," + password)
        logging.error("Login failed, check credentials: " + username + "," + password)
        return "Wrong credentials"
    else:
        logging.info("Login successful: " + username + "," + password)
        user_data = {'user_agent': user_agent, 'session_cookie': session_cookie}
        with open('accounts.txt', 'r') as f:
            old_file = literal_eval(f.read())
        old_file[username] = user_data
        with open('accounts.txt', 'w') as f:
            f.write(str(old_file))


def intialize():
    logging.info("\n\nNew log:")
    logging.info("Initializing")
    try:
        with open('accounts.txt', 'r') as f:
            f.read()
    except FileNotFoundError:
        logging.info("Config not found")
        with open('accounts.txt', 'w') as f:
            f.write('{}')
    global user_agents_amount
    with open('user_agents.txt', 'r') as f:
        user_agents_amount = len(f.readlines()) - 1
    logging.info("Available user agents: " + str(user_agents_amount))
    # for testing only
    if login_user("test", "test123", get_user_agent(2)) == "Wrong credentials":
        pass
        # Wrong credentials, do something


logging.basicConfig(filename='unbotter.log', level=logging.DEBUG,
                    format='%(asctime)s |%(levelname)s| %(message)s')
intialize()
