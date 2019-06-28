from apscheduler.schedulers.background import BackgroundScheduler
import multiprocessing as mp
import atexit
from notification.smtp import *
from notification.discord import discord_notify
from selenium import webdriver
import time
import hmac, base64, struct, hashlib
import datetime
import os
import logging
import sys
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.firefox.options import Options as FireFox_Options
from selenium.webdriver.chrome.options import Options as Chrome_Options
LOGGER.setLevel(logging.WARNING)
import configparser
from multiprocessing import Queue

q = Queue()

filename = 'trades.csv'

if os.path.exists(filename):
    pass # append if already exists
else:
    append_write = 'w' # make a new file if not
    file = open(filename,append_write)
    file.close()

class TV:
    def __init__(self,type='auto',coil_enabled=True,coil_headless=False, headless=False, browser='firefox', email_sms=True, discord_enabled=True):
        if type == 'auto':
            username = ""
            password = ""
        else:
            username = input('EMAIL ADDRESS : ')
            password = input('PASSWORD : ')
        ### COIL SUPPLEMENTAL ###
        self.coilurl = 'https://coil.com/p/nerf_herder/Python-Package-Coil-Enabled/GRn2W-j5t'
        self.ff_coil_extId = 'coilfirefoxextension@coil.com.xpi'
        ### END COIL SUPPLEMENTAL ###

        ### Drivers for
        self.gecko_source_win64 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-win64.zip'
        self.gecko_source_linux64 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz'
        self.gecko_source_linux32 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux32.tar.gz'

        self.chrome_driver74_win_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_win32.zip'
        self.chrome_driver74_mac_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_mac64.zip'
        self.chrome_driver74_linux_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_linux64.zip'

        self.chrome_driver75_win_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_win32.zip'
        self.chrome_driver75_mac_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_mac64.zip'
        self.chrome_driver75_linux_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_linux64.zip'

        self.chrome_driver76_win_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_win32.zip'
        self.chrome_driver76_mac_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_mac64.zip'
        self.chrome_driver76_linux_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_linux64.zip'

        ### Tradingview Login Page ###
        self.tvurl = 'https://www.tradingview.com/chart/d3hZBVEd/#signin'
        if coil_enabled:
            atexit.register(self._close_browser)  # AUTO CLOSE BROWSER WHEN
            ### COIL ###
            self.p1_coil = mp.Process(target=self.open_coil, args=(q, coil_headless, browser, coil_enabled))
            self.p1_coil.daemon = True
            self.p1_coil.start()
        else:
            logging.warning('Consider signing up for Coil when using tradingview-monitor as a contribution. \n Works seemlessly inside a browser.\t https://coil.com/signup ')
            ### END COIL ###


        if browser == 'firefox':
            self.get_firefox_profile_dir(headless=headless)
            self.driver = webdriver.Firefox(options=self.options, firefox_profile=str(self.data_path),executable_path=str(self.gecko))
            self.driver.get(self.tvurl)  # OPEN TRADINGVIEW URL
            self.login(username=username,password=password)

            self.alert_monitoring(email_sms=email_sms,discord_alert=discord_enabled)



    def _close_browser(self):
        q.put('goodbye')
        self.coil_driver.close()

    def file_unzip(self, file, path):
        import zipfile
        zip_ref = zipfile.ZipFile(file, 'r')
        zip_ref.extractall(path=path)
        zip_ref.close()

    def file_unzip_tar(self, file, path):
        import tarfile
        file = tarfile.open(file)
        file.extractall(path=path)
        file.close()

    def get_coil_url(self):
        return self.driver.get(self.coilurl)

    def get_tv_url(self):
        return self.tvdriver.get(self.tvurl)

    def get_firefox_profile_dir(self, headless=False, coil_enabled=False):
        from pathlib import Path
        self.gecko_path = os.path.dirname(__file__)
        self.options = FireFox_Options()
        self.options.headless = headless
        self.options.set_preference("dom.webnotifications.serviceworker.enabled", True)
        self.options.set_preference("dom.webnotifications.enabled",True)
        self.options.set_preference('permissions.default.desktop-notification', 1)

        if sys.platform in ['linux', 'linux2']:
            import subprocess

            self.ff_gecko = Path(self.gecko_path + '/geckodriver')

            bits = 'uname -m'
            ver_32_64 = subprocess.getstatusoutput(bits)

            cmd = "ls -d /home/$USER/.mozilla/firefox/*.default/"
            fp = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            FF_PRF_DIR = fp.communicate()[0][0:-2]
            self.FF_PRF_DIR_DEFAULT = str(FF_PRF_DIR, 'utf-8')


            if coil_enabled:
                ff_ext_path = os.path.join(self.FF_PRF_DIR_DEFAULT, 'extensions')
                self.ff_coil_loc = os.path.join(ff_ext_path, self.ff_coil_extId)
                ff_coil_enabled = os.path.exists(self.ff_coil_loc)
                if not ff_coil_enabled:
                    quit()

            if 'x86_64' in ver_32_64:
                if not self.ff_gecko.is_file():
                    import wget
                    self.gecko_targz = self.gecko_path + '/' + self.gecko_source_linux64.split('/')[-1]
                    wget.download(self.gecko_source_linux64, self.gecko_path)
                    self.file_unzip_tar(self.gecko_path + '/' + self.gecko_targz)
                    os.remove(self.gecko_path + '/' + self.gecko_targz)
                if self.ff_gecko.is_file():
                    self.data_path = self.FF_PRF_DIR_DEFAULT
                    self.gecko = self.ff_gecko

            if 'i368' in ver_32_64:
                if not self.ff_gecko.is_file():
                    import wget
                    self.gecko_targz = self.gecko_path + '/' + self.gecko_source_linux32.split('/')[-1]
                    wget.download(self.gecko_source_linux32, self.gecko_path)
                    self.file_unzip_tar(self.gecko_path + '/' + self.gecko_targz)
                    os.remove(self.gecko_path + '/' + self.gecko_targz)
                if self.ff_gecko.is_file():
                    self.data_path = str(self.FF_PRF_DIR_DEFAULT)
                    self.gecko = str(self.ff_gecko)

        elif sys.platform == 'win32' or 'nt':
            from pathlib import Path
            self.gecko = self.gecko_path + "\geckodriver.exe"
            self.ff_gecko = Path(self.gecko)
            mozilla_profile = os.path.join(os.getenv('APPDATA'), r'Mozilla\Firefox')
            mozilla_profile_ini = os.path.join(mozilla_profile, r'profiles.ini')
            profile = configparser.ConfigParser()
            profile.read(mozilla_profile_ini)
            self.FF_PRF_DIR_DEFAULT = os.path.normpath(os.path.join(mozilla_profile, profile.get('Profile0', 'Path')))


            if coil_enabled:
                ff_ext_path = os.path.join(self.FF_PRF_DIR_DEFAULT, 'extensions')
                self.ff_coil_loc = os.path.join(ff_ext_path, self.ff_coil_extId)
                ff_coil_enabled = os.path.exists(self.ff_coil_loc)
                if not ff_coil_enabled:
                    quit()

            ff_gecko = Path(self.gecko)
            if not ff_gecko.is_file():
                import wget
                self.gecko_win64zip = self.gecko_path + '\\' + self.gecko_source_win64.split('/')[-1]
                wget.download(self.gecko_source_win64, self.gecko_path)
                self.file_unzip(self.gecko_win64zip, self.gecko_path)
                os.remove(self.gecko_win64zip) #self.gecko_path + '\\' +

            if ff_gecko.is_file():
                self.data_path = self.FF_PRF_DIR_DEFAULT
                self.gecko = self.ff_gecko


    def get_chrome_profile_dir(self):
        from pathlib import Path
        self.chrome_driver_dir = os.path.dirname(__file__)

        if sys.platform in ['linux', 'linux2']:
            import subprocess
            self.chromedriver = 'chromedriver'
            chrome_ver = subprocess.Popen("google-chrome --version", stdout=subprocess.PIPE, universal_newlines=True,
                                          shell=True).communicate()[0]
            chrome_ver = chrome_ver.replace('Google Chrome ', '')
            chrome_ver = chrome_ver.split('.')[0]
            self.chrome_driver_file_path = self.chrome_driver_dir + self.chromedriver + chrome_ver

            if not Path.is_file(self.chrome_driver_file_path):
                import wget
                self.chrome_zip = 'chromedriver_linux64.zip'
                self.chrome_url = 'self.chrome_driver' + chrome_ver + 'linux_url'
                if chrome_ver == '76':
                    wget.download(self.chrome_driver76_linux_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.remove(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.rename('chromedriver', 'chromedriver' + chrome_ver)
                elif chrome_ver == '75':
                    wget.download(self.chrome_driver75_linux_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.remove(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.rename('chromedriver', 'chromedriver' + chrome_ver)
                elif chrome_ver == '74':
                    wget.download(self.chrome_driver74_linux_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.remove(self.chrome_driver_file_path + '/' + self.chrome_zip)
                    os.rename('chromedriver', 'chromedriver' + chrome_ver)
                    
        elif sys.platform in ['win32']:
            self.chrome_winzip = 'chromedriver_win32.zip'
            chrome_driver_exe = 'chromedriver.exe'

            self.chrome_profile = os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data\Default')
            # CHECK CHROME VERSION
            chrome_ver = os.popen(r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read()
            chrome_ver = chrome_ver.split(r'REG_SZ')[1]
            chrome_ver = chrome_ver.split('.')[0].replace(' ', '')

            if chrome_ver == '76':
                chrome_driver_ver_exe = 'chromedriver76.exe'

                if not os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):  # DOWNLOAD CHROMEDRIVER
                    import wget
                    wget.download(self.chrome_driver76_win_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_dir + '\\' + self.chrome_winzip,
                                    self.chrome_driver_dir)
                    os.rename(self.chrome_driver_dir + '\\' + chrome_driver_exe,
                              self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)
                    os.remove(self.chrome_driver_dir + '\\' + self.chrome_winzip)
                if os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):
                    self.chrome_profile = os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data')
                    self.options.add_argument("user-data-dir=" + self.chrome_profile)
                    self.driver = webdriver.Chrome(chrome_options=self.options,
                                                   executable_path=self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)

            elif chrome_ver == '75':
                chrome_driver_ver_exe = 'chromedriver75.exe'

                if not os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):  # DOWNLOAD CHROMEDRIVER
                    import wget
                    wget.download(self.chrome_driver75_win_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_dir + '\\' + self.chrome_winzip,
                                    self.chrome_driver_dir)
                    os.rename(self.chrome_driver_dir + '\\' + chrome_driver_exe,
                              self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)
                    os.remove(self.chrome_driver_dir + '\\' + self.chrome_winzip)
                if os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):
                    self.chrome_profile = os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data')
                    self.options.add_argument("user-data-dir=" + self.chrome_profile)
                    self.driver = webdriver.Chrome(chrome_options=self.options,
                                                   executable_path=self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)

            elif chrome_ver == '74':
                chrome_driver_ver_exe = 'chromedriver74.exe'
                if not os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):  # DOWNLOAD CHROMEDRIVER
                    import wget
                    wget.download(self.chrome_driver74_win_url, self.chrome_driver_dir)
                    self.file_unzip(self.chrome_driver_dir + '\\' + self.chrome_winzip, self.chrome_driver_dir)
                    os.rename(self.chrome_driver_dir + '\\' + chrome_driver_exe,
                              self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)
                    os.remove(self.chrome_driver_dir + '\\' + self.chrome_winzip)
                if os.path.isfile(self.chrome_driver_dir + '\\' + chrome_driver_ver_exe):
                    self.chrome_profile = os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data')
                    self.options.add_argument("user-data-dir=" + self.chrome_profile)
                    self.driver = webdriver.Chrome(chrome_options=self.options,
                                                   executable_path=self.chrome_driver_dir + '\\' + chrome_driver_ver_exe)

            else:
                logging.info('No Chrome browser supported')

    def click(self, button):
        page_element = self.driver.find_element_by_css_selector(button).click()
        return page_element

    def input_field(self, field, text):
        page_element = self.driver.find_element_by_css_selector(field)
        page_element.click()
        page_element.send_keys(text)
        return page_element

    def get_hotp_token(self, secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        return h

    def get_totp_token(self, secret):
        return self.get_hotp_token(secret, intervals_no=int(time.time()) // 30)

    def alert_monitoring(self, email_sms=True, discord_alert=True):
        # get the window handle after the window has opened
        main_window = self.driver.window_handles[0]
        main_window_title = self.driver.title
        print('Tradingview Page: ', str(main_window_title), '\n Monitoring {}'.format(self.tvurl))

        while True:
            try:
                alert_pair = self.driver.find_element_by_css_selector('.tv-alert-notification-dialog__title')
                alert_pair = str(alert_pair.text)
                print(alert_pair)
                # pair = alert_pair.split(' ')[-1]
                alert = self.driver.find_element_by_css_selector('.tv-alert-notification-dialog__subtitle')
                alert_descr = alert.text

                # current_window = self.driver.title
                if alert:
                    self.driver.switch_to.window(main_window)
                    print(alert.text, datetime.datetime.today())
                    if email_sms == True:
                        try:
                            send_email(alert_pair, alert_descr)
                            print('email sent')
                        except:
                            logging.warning('Failed to send email/sms')

                    if discord_alert == True:
                        try:
                            discord_notify(message=alert.text)
                        except:
                            logging.warning('Failed to send to discord')

                    # timestamp = datetime.datetime.today()
                    time.sleep(.25)
                    self.driver.find_element_by_css_selector('div[data-name*="ok"]').click()
                    time.sleep(1)
            except:
                pass

    def login(self,username='',password=''):
        #self.driver.maximize_window()
        #print(self.driver.get_window_size()) #{'width': 1936, 'height': 1176}
        self.driver.set_window_size(1936, 700)
        #### LOAD WEBPAGE ###
        time.sleep(5)
        uname = self.driver.find_element_by_name('username')
        uname.send_keys(username)
        pw = self.driver.find_element_by_name('password')
        pw.send_keys(password)
        login = self.driver.find_element_by_xpath('//span[contains(text(),\'Log In\')]/parent::button').click()
        time.sleep(3)
        print('Login Successful')


    def schedule(self):
        scheduler = BackgroundScheduler() # SCHEDULE PAGE REFRESH EVERY 5 MINS
        scheduler.add_job(self.get_coil_url, 'interval',seconds=300)
        scheduler.start()


    def open_coil(self, q, coil_headless=True, browser='firefox',coil_enabled=False):


        if browser == 'firefox':
            try: # firefox + coil
                # self.options = FireFox_Options()
                # self.options.headless = coil_headless
                self.get_firefox_profile_dir(headless=coil_headless,coil_enabled=coil_enabled)
                self.coil_driver = webdriver.Firefox(options=self.options, firefox_profile=str(self.data_path),executable_path=str(self.gecko))
                self.coil_driver.get(self.coilurl)  # OPEN URL
                self.schedule()

            except:
                logging.info('No \' Firefox Browser\' Supported for Coil')

        while True:
            if q.empty():
                pass
            else:
                print(q)
                self.driver.close()

if __name__ == '__main__':
    # send_email('test', 'test')
    start = TV(coil_enabled=True,coil_headless=False, headless=False, browser='firefox', email_sms=True, discord_enabled=True)


