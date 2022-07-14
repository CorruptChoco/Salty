# %%
# Imports
from splinter import Browser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import time as t
import re
import sqlite3
from config import email
from config import password

# %%
con = sqlite3.connect('fighter_database.db')
cur = con.cursor()
cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='fighters' ''')

# %%
# Create table
if cur.fetchone()[0]==1 : {
	print('Table exists.')
}
else:
    cur.execute('''CREATE TABLE fighters
               (name TEXT NOT NULL UNIQUE, kills INTEGER, deaths INTEGER, ratio REAL)''')

# %%
# Set the executable path and initialize Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path)
# service = Service(executable_path=ChromeDriverManager().install())
# browser = webdriver.Chrome(service=service)

# %%
#login to saltybet hit enter and wait 5 seconds for page to load
url = 'https://www.saltybet.com/authenticate?signin=1'
browser.visit(url)
#browser.find_by_id('email').click()
browser.find_by_id("email").fill(f'{email}')
browser.find_by_id("pword").fill(f'{password}\n')
# ActionChains(browser).move_to_element(text_input).send_keys_to_element(text_input, "mdicky93@gmail.com").perform()
t.sleep(3)

# %%
def update_fighters(player1_text, player2_text):
    print('update start')
    winner_banner = browser.find_by_id('betstatus').value
    print(winner_banner)
    search_phrase=re.compile('Payouts to Team Red')
    red_win = search_phrase.search(winner_banner)
    print(red_win)
    search_phrase=re.compile('Payouts to Team Blue')
    blue_win = search_phrase.search(winner_banner)
    print(blue_win)
    print(f'red was {player1_text}  blue was {player2_text}')
    # player1_name=browser.find_by_id('player1').value
    # print(player1_text)
    # print(player2_text)
    if red_win != None:
        print('red won')
        cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
        if cur.fetchone()==None:
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)", (player1_text,1,0,1.0))
            red_ratio = 1.0
        else:
            cur.execute(' SELECT kills from fighters WHERE name=?',(player1_text,))
            c_wins = cur.fetchone()[0]
            cur.execute(' SELECT deaths from fighters WHERE name=?',(player1_text,))
            c_loss = cur.fetchone()[0]
            try:
                red_ratio = (c_wins + 1) / c_loss
            except ZeroDivisionError:
                red_ratio = (c_wins + 1)
            cur.execute('UPDATE fighters SET kills = ? WHERE name = ?',(c_wins+1, player1_text))
            cur.execute('UPDATE fighters SET ratio = ? WHERE name = ?',(red_ratio, player1_text))
        cur.execute(''' SELECT * from fighters WHERE name=?''',(player2_text,))    
        if cur.fetchone()==None:   
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)", (player2_text,0,1,0.0))
            blue_ratio = 0.0
        else:
            cur.execute(' SELECT kills from fighters WHERE name=?',(player2_text,))
            c_wins = cur.fetchone()[0]
            cur.execute(' SELECT deaths from fighters WHERE name=?',(player2_text,))
            c_loss = cur.fetchone()[0]
            blue_ratio = c_wins / (c_loss + 1)
            cur.execute('UPDATE fighters SET deaths = ? WHERE name = ?',(c_loss+1, player2_text))
            cur.execute('UPDATE fighters SET ratio = ? WHERE name = ?',(blue_ratio, player2_text))
    elif blue_win != None:
        print('blue won')
        cur.execute(' SELECT * from fighters WHERE name=?',(player2_text,))
        if cur.fetchone()==None:
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)",(player2_text,1,0,1.0))
            blue_ratio = 1.0
        else:
            cur.execute(' SELECT kills from fighters WHERE name=?',(player2_text,))
            c_wins = cur.fetchone()[0]
            cur.execute(' SELECT deaths from fighters WHERE name=?',(player2_text,))
            c_loss = cur.fetchone()[0]
            try:
                blue_ratio = (c_wins + 1) / c_loss
            except ZeroDivisionError:
                blue_ratio = (c_wins + 1)
            cur.execute('UPDATE fighters SET kills = ? WHERE name = ?',(c_wins+1, player2_text))
            cur.execute('UPDATE fighters SET ratio = ? WHERE name = ?',(blue_ratio, player2_text))
        cur.execute(''' SELECT * from fighters WHERE name=?''',(player1_text,))    
        if cur.fetchone()==None:   
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)",(player1_text,0,1,0.0))
        else:
            cur.execute(' SELECT kills from fighters WHERE name=?',(player1_text,))
            c_wins = cur.fetchone()[0]
            cur.execute(' SELECT deaths from fighters WHERE name=?',(player1_text,))
            c_loss = cur.fetchone()[0]
            red_ratio = c_wins / (c_loss + 1)
            cur.execute('UPDATE fighters SET deaths = ? WHERE name = ?',(c_loss+1, player1_text))
            cur.execute('UPDATE fighters SET ratio = ? WHERE name = ?',(red_ratio, player1_text))
    con.commit()
    print('fighters updated')


# %%
def bet_loop(player1_text,player2_text):
    print('loop start')
    #check to make sure the bet was accepted before moving on
    betconfirm = browser.is_element_present_by_id('betconfirm')
    if betconfirm == True:
        #don't want to constantly keep clicking random until match starts. bet confirm appears once you bet and disappears upon match start.
        i = 0
        while betconfirm == True:
            if i == 0:
                print('bet confirmed')
            betconfirm = browser.is_element_present_by_id('betconfirm')
            t.sleep(5)
            i += 1
        #looking for the arrow in the odds section after match starts as an idicator that match is ongoing.
        i = 0
        while browser.find_by_id('betstatus').value == 'Bets are OPEN!' or browser.find_by_id('betstatus').value == 'Bets are locked until the next match.':
            t.sleep(0.2)
            if i == 0:
                print('in a match')
            i += 1
        while browser.find_by_id('betstatus').value == "":
            t.sleep(0.10)
        while browser.find_by_id('betstatus').value == None:
            t.sleep(0.10)
        print('fighters to be updated')
        update_fighters(player1_text,player2_text)
    else:
        print('bet not confirmed')
        t.sleep(2)
    print('loop complete')

# %%
def bet_who(bet_amount):
    print('begin selection')
    player1 = browser.find_by_id('player1')
    player1_text = browser.find_by_id('player1').value
    # print(player1_text)
    player2 = browser.find_by_id('player2')
    player2_text = browser.find_by_id('player2').value
    # print(player2_text)
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
        try:
            #had to use a try except here as clicking when nothing is there causes errors. I'm sure this can be written better. this finds and clicks all in button
            allin=browser.find_by_id(bet_amount)
            allin.click()
            t.sleep(0.2)
            #random click of red or blue.
            coinflip=random.choice([0,1])
            if coinflip == 1:
                player2.click()
                print('bet on blue')
                t.sleep(0.2)
            else:
                player1.click()
                print('bet on red')
                t.sleep(0.2)
            print('go to loop')
            bet_loop(player1_text,player2_text)
        except:
            t.sleep(1)
            # probably need to define a function for random then put here to retry random() after sleep
    elif (fighter1_present == 1 and fighter2_present == 0) or (fighter1_present == 0 and fighter2_present == 1):
        try:
            allin=browser.find_by_id(bet_amount)
            allin.click()
            cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
            if cur.fetchone()==None:
                cur.execute(' SELECT ratio from fighters WHERE name=?',(player2_text,))
                ratio = cur.fetchone()[0]
                print(f'player 2 ratio is {ratio}')
                if ratio < 1.0:
                    player1.click()
                    print('bet on red')
                    t.sleep(0.2)
                else:
                    player2.click()
                    print('bet on blue')
                    t.sleep(0.2)
            else:
                cur.execute(' SELECT ratio from fighters WHERE name=?',(player1_text,))
                ratio = cur.fetchone()[0]
                print(f'player 1 ratio is {ratio}')
                if ratio < 1.0:
                    player2.click()
                    print('bet on blue')
                    t.sleep(0.2)
                else:
                    player1.click()
                    print('bet on red')
                    t.sleep(0.2)
            print('go to loop')
            bet_loop(player1_text,player2_text)
        except:
            t.sleep(1)
        # bet on fighter with stats if ratio >0.5 else bet on unknown
    elif fighter1_present == 1 and fighter2_present == 1:
        # bet on fighter with higher win loss ratio
        try:
            allin=browser.find_by_id(bet_amount)
            allin.click()
            cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,)) 
            red_ratio = cur.fetchone()[0]
            print(f'red ratio is {red_ratio}')
            cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,))
            blue_ratio = cur.fetchone()[0]
            print(f'blue ratio is {blue_ratio}')
            if red_ratio >= blue_ratio:
                player1.click()
                print('bet on red')
            else:
                player2.click()
                print('bet on blue')
            print('go to loop')
            bet_loop(player1_text,player2_text)
        except:
            t.sleep(1)
    print('finish selection')

# %%
u_input = int(input('How many matches would you like to run?'))
while browser.find_by_id('betstatus').value != 'Bets are OPEN!':
    t.sleep(5)
random.seed()
for i in range(u_input):
    while browser.find_by_id('betstatus').value != 'Bets are OPEN!':
        t.sleep(1)
    #t_time = browser.is_element_present_by_id('tournament-note')
    #used is_element_not instead of is_element_present as it runs almost 2 seconds faster, don't know why.
    t_time = browser.is_element_not_present_by_css('span[class="dollar purpletext"][id="balance"]')
    #if the purple text of balance is present we begin betting
    if t_time == False and int(browser.find_by_id('balance').value.replace(',',"")) <=4000:
        print(f'{i} tournament all in')
        print(browser.find_by_id('balance').value)
        bet_who('interval10')
    elif t_time == False and int(browser.find_by_id('balance').value.replace(',',"")) <=7000:
        print(f'{i} tournament 50 percent')
        print(browser.find_by_id('balance').value)
        bet_who('interval5')
    elif t_time == False and int(browser.find_by_id('balance').value.replace(',',"")) > 7000:
        print(f'{i} tournament 10 percent')
        print(browser.find_by_id('balance').value)
        bet_who('interval1')    
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 500:
        print(f'{i} regular all in')
        print(browser.find_by_id('balance').value)
        bet_who('interval10')
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 1000 :
        print(f'{i} regular half bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval5')
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 2000 :
        print(f'{i} regular 30 percent bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval3')
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 3000 :
        print(f'{i} regular 20 percent bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval2')
    else:
        print(f'{i} regular 10 percent bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1')
browser.quit()
con.close()


