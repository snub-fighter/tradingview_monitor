from selenium import webdriver
import time
import hmac, base64, struct, hashlib
import datetime
import os
import csv
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)
import ccxt

filename = 'trades.csv'

if os.path.exists(filename):
    pass # append if already exists
else:
    append_write = 'w' # make a new file if not
    file = open(filename,append_write)
    file.close()

url = 'https://www.tradingview.com/chart/d3hZBVEd/#signin'

def creds(type='auto'):
    if type == 'auto':
        username = ""
        password = ""
        return username, password
    else:
        username = input('EMAIL ADDRESS : ')
        password = input('PASSWORD : ')
        return  username, password
time.sleep(2)

username, password = creds(type='auto')




def start():
    from trade import trader
    trader = trader()


    def get_hotp_token(secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        return h

    def get_totp_token(secret):
        return get_hotp_token(secret, intervals_no=int(time.time()) // 30)

    def click(button):
        page_element = driver.find_element_by_css_selector(button).click()
        return page_element

    def input_field(field, text):
        page_element = driver.find_element_by_css_selector(field)
        page_element.click()
        page_element.send_keys(text)
        return page_element

    def write_csv(row, pair,interval):

        filename = 'trades_' + pair+'_'+interval+'.csv'
        if os.path.exists(filename):
            pass # append if already exists
        else:
            append_write = 'w' # make a new file if not
            file = open(filename,append_write)
            file.close()
        with open(filename, 'a', newline='') as writeFile:
                        writer = csv.writer(writeFile)
                        writer.writerow(row)
                        writeFile.close()

    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=OFF')
        #chrome_options.add_argument('headless')
        prefs = {"profile.default_content_setting_values.notifications" : 1}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome('./chromedriver75_beta.exe',options=chrome_options)#,chrome_options='--no-startup-window'
        print('Current Chrome Version is 75')
    except:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=OFF')
        #chrome_options.add_argument('headless')
        prefs = {"profile.default_content_setting_values.notifications" : 1}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome('./chromedriver74.exe',options=chrome_options)
        print('Current Chrome Version is 74')

    driver.maximize_window()
    #### LOAD WEBPAGE ###
    driver.get(url)
    time.sleep(5)

    uname = driver.find_element_by_name('username')
    uname.send_keys(username)
    pw = driver.find_element_by_name('password')
    pw.send_keys(password)
    login = driver.find_element_by_xpath('//span[contains(text(),\'Log In\')]/parent::button').click()
    time.sleep(3)
    print('Login Successful')
    #get the window handle after the window has opened
    main_window = driver.window_handles[0]
    main_window_title = driver.title
    print('Tradingview Page: ', str(main_window_title), '\n Monitoring {}'.format(url))
    while True:
        #SELL: PYTHON - MG Sell Alert
        #BUY: PYTHON - MG Buy Alert
        try:
            alert_pair = driver.find_element_by_css_selector('.tv-alert-notification-dialog__title')
            alert_pair = alert_pair.text
            alert_, on, pair = alert_pair.split(' ')
            pair.strip()
            print('\nCall this pair to be traded on: ', pair)
            alert = driver.find_element_by_css_selector('.tv-alert-notification-dialog__subtitle')
            current_window = driver.title
            if alert:
                bid, ask = trader.binance_orderbook(symbol='XRP/USDT')
                bid = bid[0][0]
                ask = ask[0][0]
                driver.switch_to.window(main_window)
                print(alert.text, datetime.datetime.today())
                timestamp = datetime.datetime.today()
                if 'MGv6' in alert.text and 'BUY' in alert.text:
                    indicator, exchange, buysell, pair, interval = alert.text.split('-')
                    print(timestamp, indicator, exchange, buysell, pair, interval,  'Best Price: ',ask)
                    print('Pseudo Trade at price --> ', ask, '\n')

                    row = [str(timestamp),str(indicator), str(exchange), str(buysell), str(pair), str(interval), str(ask)]
                    write_csv(row, pair,interval)
                elif 'MGv6' in alert.text and 'SELL' in alert.text:
                #elif alert.text =='MGv6-BINANCE-BUY-XRPBNB-1M':
                    indicator, exchange, buysell, pair, interval = alert.text.split('-')
                    print(timestamp, indicator, exchange, buysell, pair, interval, 'Best Price: ',bid)
                    print('Pseudo Trade at price --> ', bid, '\n')

                    #getattr(trader, binance_trade)(symbol='XRP/BNB', amount=500, order_type='market',buy_sell=buysell)
                    row = [str(timestamp),str(indicator), str(exchange), str(buysell), str(pair), str(interval), str(bid)]
                    write_csv(row, pair,interval)
                time.sleep(.25)
                driver.find_element_by_css_selector('div[data-name*="ok"]').click()
                #driver.find_element_by_css_selector('.js-dialog.action-click.js-dialog.no-drag.tv-button.tv-button--primary')
                time.sleep(1)
                #<div data-name="ok" class="js-dialog__action-click js-dialog__no-drag tv-button tv-button--primary">OK</div>
        except:
            pass


if __name__ == '__main__':
    start()


