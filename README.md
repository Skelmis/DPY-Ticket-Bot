# DPY-Ticket-Bot
A fully featured ticket bot coded in discord.py

This bot features, logging of ticket contents & support for reactions as well as creating tickets via the standard command line. 

---

## Usage
- Run the following
  - `pip install aiosqlite`
  - `pip install discord.py==1.7.3`
- Add your own bot token [here](https://github.com/Skelmis/DPY-Ticket-Bot/blob/master/bot_config/)
- Modify the 4 lines found [here](https://github.com/Skelmis/DPY-Ticket-Bot/blob/master/bot.py#L38) to include your own relevant id's 
- Run the `setup` command, and your good to go!

Requires python 3.8 or higher


## Version

**4**

Changes from last version:
 - Sqlite is now the default storage
   - If you previously used Json. You will need to migrate your data or
     simply change the bot to continue using Json. See `bot.py` for this.
 - If you attempt to close tickets when using Json and you haven't run
   the setup command yet the bot will 'warn' before continuing.
 - Adding logging by default