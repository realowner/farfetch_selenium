from parts.Browser import Browser
from parts.LoginData import LoginData
from parts.GetProxy import GetProxy

import time

def check(ip, port):
    logins = LoginData.from_txt('login_data.txt')

    test = 'point'

    browser = Browser.my_browser(ip, port)
    try:
        print('= LOGIN PAGE =')
        try:
            browser.get('https://www.farfetch.com/ua/login.aspx')
            login_input = browser.find_element_by_id('email-input-login')
            login_input.send_keys('someofus@mail.ru')
            time.sleep(3)
            pass_input = browser.find_element_by_id('password-input-login')
            pass_input.send_keys('1Qzxc12345')
            responce = 'done'
            time.sleep(10)
        except:
            responce = 'error'
        
        print('--> ' + responce)

    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


check(ip=None, port=None)
