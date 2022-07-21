# Richard Bot

## Description
I mostly did this for fun and just to challenge myself. I just completed a short bootcamp that dealt with data analytics where python and other topics were touched on. I am NOT a professional and give no guarantees about the state or viability of my coding.

I created this bot to auto-bet on the website "saltybet.com" It was done entirely with python for code and SQLite as a database. There are currently 2 version I have up. "Richard_Bot" is the self betting python code that will bet on its own. "Random Tournament Only" is a separate thing that runs random betting during a saltybet tournament only. I use this on my main account when I am too busy to play myself so I can have extra money to play around with on my account.

## How it works
1. Richard (the bot) begins by opening up the log in page to saltybet.
2. Richard then fills in page with the login information contained within the config.py file (you will need to provide your own) then hits enter to bring you to the main saltybet page.
3. Richard asks you how many matches you want it to run for. (you have to enter a numerical value)
4. Richard decides which button on the bottom of your screen to click. This decides how much is bet. Richard chooses how much to bet based on 2 things. How much money you have and whether or not there is a tournament currently happening. The amounts bet are as follows

| Regular Money | Amount Bet | Tournament Money | Amount Bet |
| :------: |:------:| :-----:| :-------: |
| <=500 | all in | <=4000 | all in |
| <=1,000 | 50% | <=7000 | 50% |
| <=2,000 | 30% | >7000 | 10% |
| <=3,000 | 20% | | |
| <=250,000 | 10% | | |
| <=500,000 | 5% | | |
| <=2,000,000| 2.5% | | |
| <=3,500,000| 1.25% | | |
| <=5,000,000| 1.00% | | |
| >5,000,000| 0.80% | | |

5. Richard then decides who he is going to bet on. There are 3 cases possible.
    *  Neither fighter is found in the database (which is currently still expanding as I run it.) in this case, Random bet.

    * One fighter is found other is not. If found fighter's win/loss ratio is >=1 Richard will bet on that fighter. If not he will bet on the unknown.

    * Both fighters are found. Richard will bet on the fighter with the greater win/loss ratio. If they are the same it will bet on Red. (cause I like red, why not)

6. Richard will wait until the match is complete and sees who wins the match.
7. Richard updates the database with the fighters new stats or inserts the new fighter with stats.
8. Richard begins the loop again and continues until it has gone the requested number of matches.
9. Richard closes the browser window and connection to the database.

## Installation
1. You need a couple of modules installed in Python. I don't plan on going over them here you can look them up and how to install them. (Mostly just pip install "item" from command line)
    * splinter  https://splinter.readthedocs.io/en/latest/install.html
    * selenium  https://pypi.org/project/webdriver-manager/
    * sqlite3, re, time, random, all installed in python by default
    * you may need to add sqlite to PATH  https://stackoverflow.com/questions/29042954/sqlite-path-environment-variable-db-browser-sqlite

2. make a saltybet.com account.

3. you will need to make a config.py file and place it with Richard bot with the following in it.
    email = "your login email to saltybet"
    password = "your login password to saltybet"
4. Run the Richard bot file.
5. I personally use SQLiteStudio as a GUI for my database as an easy way to look at it.
6. I personally use Visual Studio Code to write files and run .ipynb files.

*** also note to anyone using this. currently to stop this during running in jupyter notebooks it often requires restarting the kernal. idk why, working on it.

## Known Issues
1. If you open Richard during betting for an exhibition match he will bet on that match as though it was a normal match.
2. It is possible for the video of saltybet to lag behind the html updates so that the match finishes while the video of the previous match is ongoing. This happens in my experience when running other programs like games. This causes Richard to not update the database and just go on to the next match. The temporary fix is to just refresh the page to allow the video to sync up. Or you could try changing the code to run in headless mode to avoid completely (unsure of this fix).

## Updates
### 7/21/2022  
- Richard will now only bet during exhibition matches if you have >50,000. He will bet 1,000 randomly. These fights are not logged in the Database.
- Also updated the amounts bet during regular matches to account for larger amounts of money in balance.
- Added a tracker that prints statistics every 10 matches.
- fixed a bug that was effecting fights when both fighters are found.

*** all the printing it does to the console currently if for debugging purposes.

*** the python only version of Richard still throws some error but it seems they can be ignored from online sources. The code still works.