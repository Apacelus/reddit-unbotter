# reddit-unbotter
Anti detection tool for bot masters. Pretends to be human, to prevent reddit from flagging accounts as bots/spam.  
In active developement.
## Concept
When first run, the accounts will subscribe to 10-15 random popular subreddits.
The accounts visit reddit at a regular time(±30 min) and browse it. They will do the following actions:
- view posts
- upvote(often) 
- downvote(rare) 
- comment(very rare)
## Settings
- Activeness(how often the account will visit reddit):
  - 0: Very rarely active account, ~1 hour per month
  - 1: Rarely active account, ~1-2 hours every 2 weeks
  - 2: Casual account, ~30min every 2-3 days
  - 3(default): Normal account, ~1 hour every day
  - 4: Highly active account, ~2-3 hours per day, multiple sessions
  - 5: Extremely active account, ~3-5 hours per day, multiple sessions  

- Vote-ratio(upvote/downvote ratio. Enter 80 for 80/20 ratio, aka 80% upvote, 20% downvote chance). Default: 90/10  
- Vote-chance(the chance to vote on a post). Default: 40  
- Leave-comment-chance(chance to leave a comment on a post). Default: 5  
## To-do:
- [x] Selenium implementation
- [x] Login
- [ ] Simple reddit "browsing"
- [ ] Post + comment up/downvote
- [ ] Commenting
- [ ] Human behavior imitation
- [ ] Tor network routing
