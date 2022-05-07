# reddit-unbotter
Anti detection tool for bot masters. Pretends to be human, so reddit doesnt flag the accounts as a bot accounts.  
**Development will contnue mid Q3 2022**
## Concept
When first run, the accounts will subscribe to 10-15 random popular subreddits.
The accounts go to reddit at a regular time(±30 min) and browse it. They will do the following actions:
- view posts
- upvote(often) 
- downvote(rare) 
- comment(only once in a few days)
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
- [ ] Schedule implementation
- [ ] Simple reddit "browsing"
- [ ] Post up/downvote
- [ ] Comment up/downvore
- [ ] Commenting
- [ ] Tor implementation
