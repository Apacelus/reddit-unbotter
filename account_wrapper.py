import requests


def get_session_cookie(username, password, useragent):
    login_data = {
        'user': username,
        'passwd': password,
        'rem': 'on',
    }
    login_request = requests.post('https://old.reddit.com/api/login/' + "username",
                                  headers={"User-Agent": useragent[2:len(useragent) - 3]}, data=login_data,
                                  cookies={"edgebucket": "nyE3MhZ1hfZKBcEYVY"})
    reddit_session = login_request.cookies.get("reddit_session")
    return reddit_session


def view_post(post_id):
    pass


def join_subreddit(subreddit_id):
    pass


def vote_post(post_id, vote_type):
    pass
