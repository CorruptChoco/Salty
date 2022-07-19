# %%
#tell me who to bet for.
import sqlite3
import random
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

# %%
con = sqlite3.connect('fighter_database.db')
cur = con.cursor()
cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='fighters' ''')

# %%
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=True)
url = 'https://www.saltybet.com'
browser.visit(url)

# %%
random.seed()
player1 = browser.find_by_id('player1')
player1_text = browser.find_by_id('player1').value
player2 = browser.find_by_id('player2')
player2_text = browser.find_by_id('player2').value
cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
if cur.fetchone()==None:
    print('fighter 1 not found')
    fighter1_present=0
else:
    print('fighter 1 found')
    fighter1_present=1
cur.execute(' SELECT * from fighters WHERE name=?',(player2_text,))
if cur.fetchone()==None:
    print('fighter 2 not found')
    fighter2_present=0
else:
    print('fighter 2 found')
    fighter2_present=1
if fighter1_present == 0 and fighter2_present == 0:
    # random fight.
    coinflip=random.choice([0,1])
    if coinflip == 1:
        print('bet on blue')
    else:
        print('bet on red')
elif (fighter1_present == 1 and fighter2_present == 0) or (fighter1_present == 0 and fighter2_present == 1):
    cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
    if cur.fetchone()==None:
        cur.execute(' SELECT ratio from fighters WHERE name=?',(player2_text,))
        ratio = cur.fetchone()[0]
        print(f'player 2 ratio is {ratio}')
        if ratio < 1.0:
            print('bet on red')
        else:
            player2.click()
            print('bet on blue')
    else:
        cur.execute(' SELECT ratio from fighters WHERE name=?',(player1_text,))
        ratio = cur.fetchone()[0]
        print(f'player 1 ratio is {ratio}')
        if ratio < 1.0:
            print('bet on blue')
        else:
            print('bet on red')
    # bet on fighter with stats if ratio >0.5 else bet on unknown
elif fighter1_present == 1 and fighter2_present == 1:
    # bet on fighter with higher win loss ratio
    cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,)) 
    red_ratio = cur.fetchone()[0]
    print(f'red ratio is {red_ratio}')
    cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,))
    blue_ratio = cur.fetchone()[0]
    print(f'blue ratio is {blue_ratio}')
    if red_ratio >= blue_ratio:
        print('bet on red')
    else:
        print('bet on blue')
browser.quit()
con.close()


