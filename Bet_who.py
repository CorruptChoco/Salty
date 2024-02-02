# %%
#tell me who to bet for.
import pyautogui
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
    #print('fighter 1 not found')
    fighter1_present=0
else:
    #print('fighter 1 found')
    fighter1_present=1
cur.execute(' SELECT * from fighters WHERE name=?',(player2_text,))
if cur.fetchone()==None:
    #print('fighter 2 not found')
    fighter2_present=0
else:
    #print('fighter 2 found')
    fighter2_present=1
if fighter1_present == 0 and fighter2_present == 0:
    # random fight.
    coinflip=random.choice([0,1])
    if coinflip == 1:
        pyautogui.alert(f'Random Fight\n'
            f'Bet on blue')
    else:
        pyautogui.alert(f'Random Fight\n'
            f'Bet on Red')
elif (fighter1_present == 1 and fighter2_present == 0) or (fighter1_present == 0 and fighter2_present == 1):
    cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
    if cur.fetchone()==None:
        cur.execute(' SELECT ratio from fighters WHERE name=?',(player2_text,))
        ratio = cur.fetchone()[0]
        #print(f'player 2 ratio is {ratio}')
        if ratio < 1.0:
            pyautogui.alert(f'Blue Fighter Found\n'
                f'Blue Ratio is {ratio}\n'
                f'Bet on Red')
        else:
            player2.click()
            pyautogui.alert(f'Blue Fighter Found\n'
                f'Blue Ratio is {ratio}\n'
                f'Bet on Blue')
    else:
        cur.execute(' SELECT ratio from fighters WHERE name=?',(player1_text,))
        ratio = cur.fetchone()[0]
        #print(f'player 1 ratio is {ratio}')
        if ratio < 1.0:
            pyautogui.alert(f'Red Fighter Found\n'
                f'Red Ratio is {ratio}\n'
                f'Bet on Blue')
        else:
            pyautogui.alert(f'Red Fighter Found\n'
                f'Red Ratio is {ratio}\n'
                f'Bet on Red')
    # bet on fighter with stats if ratio >0.5 else bet on unknown
elif fighter1_present == 1 and fighter2_present == 1:
    # bet on fighter with higher win loss ratio
    cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,)) 
    red_ratio = cur.fetchone()[0]
    #print(f'red ratio is {red_ratio}')
    cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player2_text,))
    blue_ratio = cur.fetchone()[0]
    #print(f'blue ratio is {blue_ratio}')
    if red_ratio >= blue_ratio:
        pyautogui.alert(f'Both Fighters Found\n'
            f'Red Ration is {red_ratio}\n'
            f'Blue Ratio is {blue_ratio}\n'
            f'Bet on Red')
    else:
        pyautogui.alert(f'Both Fighters Found\n'
            f'Red Ration is {red_ratio}\n'
            f'Blue Ratio is {blue_ratio}\n'
            f'Bet on Red')
browser.quit()
con.close()



# %%
