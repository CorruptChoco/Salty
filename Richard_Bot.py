# %%
# Imports
from splinter import Browser
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
browser = Browser('chrome', **executable_path, headless=False)

# %%
#login to saltybet hit enter and wait 3 seconds for page to load
url = 'https://www.saltybet.com/authenticate?signin=1'
browser.visit(url)
#browser.find_by_id('email').click()
browser.find_by_id("email").fill(f'{email}')
browser.find_by_id("pword").fill(f'{password}\n')
# ActionChains(browser).move_to_element(text_input).send_keys_to_element(text_input, "mdicky93@gmail.com").perform()
t.sleep(3)

# %%
def cor_percent():
    global correct_bet
    error_catch = 0
    winner_banner = browser.find_by_id('betstatus').value
    red_win = re.search('Payouts to Team Red', winner_banner)
    blue_win = re.search('Payouts to Team Blue', winner_banner)
    try:
        bet_red = browser.find_by_id("lastbet").find_by_css("span")[0].has_class('redtext')
        bet_blue = browser.find_by_id("lastbet").find_by_css("span")[0].has_class('bluetext')
        green_confirm = browser.find_by_id("lastbet").find_by_css("span")[1].has_class('greentext')
    except:
        error_catch = 1
    if error_catch != 1:
        if bet_red == True and green_confirm == True and red_win != None:
            correct_bet = 1
        elif bet_red == True and green_confirm == True and red_win == None:
            correct_bet = 0
        elif bet_blue == True and green_confirm == True and blue_win != None:
            correct_bet = 1
        elif bet_blue == True and green_confirm == True and blue_win == None:
            correct_bet = 0

# %%
def update_fighters(player1_text, player2_text):
    print('update start')
    winner_banner = browser.find_by_id('betstatus').value
    print(winner_banner)
    red_win = re.search('Payouts to Team Red', winner_banner)
    print(red_win)
    blue_win = re.search('Payouts to Team Blue', winner_banner)
    print(blue_win)
    print(f'red was {player1_text}  blue was {player2_text}')
    if red_win != None:
        print('red won')
        cur.execute(' SELECT * from fighters WHERE name=?',(player1_text,))
        if cur.fetchone()==None:
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)", (player1_text,1,0,1.0))
            red_ratio = 1.0
        else:
            cur.execute(' SELECT kills, deaths from fighters WHERE name=?',(player1_text,))
            c_wins, c_loss = cur.fetchone()
            try:
                red_ratio = (c_wins + 1) / c_loss
            except ZeroDivisionError:
                red_ratio = (c_wins + 1)
            cur.execute('UPDATE fighters SET kills = ?, ratio = ? WHERE name = ?',(c_wins+1, red_ratio, player1_text))
        cur.execute(''' SELECT * from fighters WHERE name=?''',(player2_text,))    
        if cur.fetchone()==None:   
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)", (player2_text,0,1,0.0))
            blue_ratio = 0.0
        else:
            cur.execute(' SELECT kills, deaths from fighters WHERE name=?',(player2_text,))
            c_wins, c_loss = cur.fetchone()
            blue_ratio = c_wins / (c_loss + 1)
            cur.execute('UPDATE fighters SET deaths = ? , ratio = ? WHERE name = ?',(c_loss+1, blue_ratio, player2_text))
    elif blue_win != None:
        print('blue won')
        cur.execute(' SELECT * from fighters WHERE name=?',(player2_text,))
        if cur.fetchone()==None:
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)",(player2_text,1,0,1.0))
            blue_ratio = 1.0
        else:
            cur.execute(' SELECT kills, deaths from fighters WHERE name=?',(player2_text,))
            c_wins, c_loss = cur.fetchone()
            try:
                blue_ratio = (c_wins + 1) / c_loss
            except ZeroDivisionError:
                blue_ratio = (c_wins + 1)
            cur.execute('UPDATE fighters SET kills = ?, ratio = ? WHERE name = ?',(c_wins+1, blue_ratio, player2_text))
        cur.execute(''' SELECT * from fighters WHERE name=?''',(player1_text,))    
        if cur.fetchone()==None:   
            cur.execute("INSERT INTO fighters VALUES (?,?,?,?)",(player1_text,0,1,0.0))
        else:
            cur.execute(' SELECT kills, deaths from fighters WHERE name=?',(player1_text,))
            c_wins, c_loss = cur.fetchone()
            red_ratio = c_wins / (c_loss + 1)
            cur.execute('UPDATE fighters SET deaths = ? , ratio = ? WHERE name = ?',(c_loss+1, red_ratio, player1_text))
    con.commit()
    print('fighters updated')
    cor_percent()

# %%
def bet_loop(player1_text,player2_text, exhib_marker):
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
        if exhib_marker == 1:
            return
        else:
            update_fighters(player1_text,player2_text)
    else:
        print('bet not confirmed')
        t.sleep(2)
    print('loop complete')

# %%
def bet_who(bet_amount, mo_money = 0):
    print('begin selection')
    player1 = browser.find_by_id('player1')
    player1_text = browser.find_by_id('player1').value
    # print(player1_text)
    player2 = browser.find_by_id('player2')
    player2_text = browser.find_by_id('player2').value
    balance = int(browser.find_by_id('balance').value.replace(',',""))
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
            if mo_money == 0:
                allin=browser.find_by_id(bet_amount)
                allin.click()
                t.sleep(0.2)
            else:
                browser.find_by_id('wager').fill(str(round(balance * mo_money)))
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
            exhib_marker = 0
            bet_loop(player1_text,player2_text, exhib_marker)
        except:
            t.sleep(1)
            # probably need to define a function for random then put here to retry random() after sleep
    elif (fighter1_present == 1 and fighter2_present == 0) or (fighter1_present == 0 and fighter2_present == 1):
        try:
            if mo_money == 0:
                allin=browser.find_by_id(bet_amount)
                allin.click()
                t.sleep(0.2)
            else:
                browser.find_by_id('wager').fill(str(round(balance * mo_money)))
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
            exhib_marker = 0
            bet_loop(player1_text,player2_text, exhib_marker)
        except:
            t.sleep(1)
        # bet on fighter with stats if ratio >0.5 else bet on unknown
    elif fighter1_present == 1 and fighter2_present == 1:
        # bet on fighter with higher win loss ratio
        try:
            if mo_money == 0:
                allin=browser.find_by_id(bet_amount)
                allin.click()
                t.sleep(0.2)
            else:
                browser.find_by_id('wager').fill(str(round(balance * mo_money)))
            cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player1_text,)) 
            red_ratio = cur.fetchone()[0]
            print(f'red ratio is {red_ratio}')
            cur.execute(''' SELECT ratio from fighters WHERE name=?''',(player2_text,))
            blue_ratio = cur.fetchone()[0]
            print(f'blue ratio is {blue_ratio}')
            if red_ratio >= blue_ratio:
                player1.click()
                print('bet on red')
            else:
                player2.click()
                print('bet on blue')
            print('go to loop')
            exhib_marker = 0
            bet_loop(player1_text,player2_text, exhib_marker)
        except:
            t.sleep(1)
    print('finish selection')

# %%
def exhib_bet():
    player1 = browser.find_by_id('player1')
    player1_text = browser.find_by_id('player1').value
    player2 = browser.find_by_id('player2')
    player2_text = browser.find_by_id('player2').value
    browser.find_by_id('wager').fill('1000')
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
    t.sleep(0.2)
    exhib_marker = 1
    bet_loop(player1_text,player2_text, exhib_marker)
        
   

# %%
def print_stats():
    print(times_correct)
    print(f'total number of matches: {u_input}')
    print(f'number of correct guesses: {times_correct.count(1)}')
    print(f'number of incorrect guesses: {times_correct.count(0)}')
    print(f'number of errors: {times_correct.count(2)}')
    try:
        print(f'percentage of right guesses: {round((times_correct.count(1)/(times_correct.count(1)+times_correct.count(0)))*100, 2)}%')        
    except ZeroDivisionError:
        print('no regular matches run yet')

# %%
u_input = int(input('How many matches would you like to run?'))
while browser.find_by_id('betstatus').value != 'Bets are OPEN!':
    t.sleep(5)
times_correct = []
random.seed()
for i in range(u_input):
    while browser.find_by_id('betstatus').value != 'Bets are OPEN!':
        t.sleep(1)
    remove_stats = 0
    correct_bet = 2
    footer_text = browser.evaluate_script("document.getElementById('footer-alert').textContent")
    exhib_time = re.search('exhibition', footer_text, re.I)
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
    elif exhib_time != None and int(browser.find_by_id('balance').value.replace(',',"")) >=50000:
        print(f'{1} exhhibition bet')
        print(browser.find_by_id('balance').value)
        remove_stats = 1
        exhib_bet()
    elif exhib_time != None and int(browser.find_by_id('balance').value.replace(',',"")) <50000:
        y=0
        while exhib_time != None:
            if y== 0:
                print("exhibition not enough money")
                print(browser.find_by_id('balance').value)
                y += 1
            footer_text = browser.evaluate_script("document.getElementById('footer-alert').textContent")
            exhib_time = re.search('exhibition', footer_text, re.I)
            t.sleep(20)    
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
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 250000 :
        print(f'{i} regular 10 percent bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1')
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 500000 :
        print(f'{i} regular 5% bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1', 0.05)
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 2000000 :
        print(f'{i} regular 2.5% bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1', 0.025)
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 3500000 :
        print(f'{i} regular 1.25% bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1', 0.0125)
    elif int(browser.find_by_css('span[class="dollar"][id="balance"]').value.replace(',',"")) <= 5000000 :
        print(f'{i} regular 1.00% bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1', 0.01)
    else:
        print(f'{i} regular 0.8% bet')
        print(browser.find_by_id('balance').value)
        bet_who('interval1', 0.008)
    if remove_stats == 0:
        times_correct.append(correct_bet)
    if (i + 1) % 10 == 0:
        print_stats()
browser.quit()
con.close()


