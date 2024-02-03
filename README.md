# commands
This discord bot just has three commands:
1. get - which gives you a message from the cheat sheet (the title is the first line).
2. reload - which reloads the cheat sheet (permited only to the user with the ID in me inside of the .env file).
3. view-code - sends a message with a url to this page

# making it work
you need to add a .env file with the following data:
```
# the discod bot's token:
TOKEN=

# The offical server id (server with the cheat sheet):
OFFICIAL_SERVER_ID=

# The cheat sheet channel id
OFFICIAL_CHANNEL_ID=

# YOUR ID, (used to save cheat sheet incase something's wrong)
ME=
```
