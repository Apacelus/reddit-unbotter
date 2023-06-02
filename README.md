# reddit-unbotter

Anti detection tool for bot masters. Pretends to be human to prevent reddit from flagging accounts as bots/spam.  
Project is not yet ready for use.

## Concept

This script employs the following tactics to evade bot detection:

1. Use selenium to control a custom firefox browser, which has been modified to remove the webdriver flag (which can be
   used by websites to detect automation tools)
2. Use different proxies for accounts
3. Log in at different times with the reddit accounts
4. Use different aspect resolutions/aspect ratios
5. Upvote/downvote, read/write small comments to mimic a real user
6. Carries over all cookies every time the bot browses reddit, instead of logging in each time
7. Guide the mouse to a non-precise location in a non-precise manner, instead of clicking the button with selenium