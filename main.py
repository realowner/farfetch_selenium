from parts.Browser import Browser
from parts.MobileBrowser import MobileBrowser
from parts.GetProxy import GetProxy
from database.DatabaseModel import OrdersModel
import requests

import time
import json

# testing db conn
def db_check():
    all_info = OrdersModel.select().get()

    row_id = all_info.id
    OrdersModel.update_with_status_3(id=row_id)


def check(ip, port, model):

    browser = Browser.my_browser(ip, port)
    try:
  
        try:
            browser.get('https://www.farfetch.com/ua/useraccount.aspx')
            login_input = browser.find_element_by_id('email-input-login')
            login_input.send_keys(model.email)
            time.sleep(3)
            pass_input = browser.find_element_by_id('password-input-login')
            pass_input.send_keys(model.password)
            time.sleep(3)
            checkbox = browser.find_element_by_id('RememberMe')

            # метод click() приводит к ошибке при нажатии на чекбокс
            browser.execute_script("arguments[0].click();", checkbox) 
            time.sleep(3)

            # поиск по xpath, id или class не подходит
            login_btn = browser.find_element_by_xpath('/html/body/div[3]/main/section/div[2]/div/div/div[1]/div[1]/div/form/div[7]/button')
            login_btn.click()
            time.sleep(3)

            cookie = browser.get_cookies()
            cookie_str = Browser.gen_cookie(cookie)
            headers = {'cookie': cookie_str}

            r = requests.get('https://www.farfetch.com/ua/ajax/userdetails', headers=headers)
            res = r.json()
            i=0

            # Получение адреса
            # browser.get('https://www.farfetch.com/ua/addressbook/')
            # address = json.loads(browser.find_element_by_id("json").text)
            # try:
            #     address = json.loads(browser.find_element_by_id("json").text)
            #     model.set_country(address)
            # except Exception as expt:
            #     print('Не удалось получить данные по адресу')
            #     model.set_status(4)
            # print(address)


            # browser.get('https://www.farfetch.com/ua/ajax/userdetails')
            # time.sleep(3)
            #
            browser.get('https://www.farfetch.com/ua/orders/')
            content = json.loads(browser.find_element_by_id("json").text)
            # print(json.loads(browser.find_element_by_id("json").text))

            time.sleep(20)
        except Exception as expt:
            print(expt)
        
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


if __name__ == '__main__':
    model = OrdersModel.get_by_email('Anthonyroberts@me.com')
    # models = OrdersModel.get_by_status(1)
    # i=0
    # model.__setattr__('countryCode', 'ru_RU')
    # model.save()
    # i=0
    # ip, port = None. Для работы с прокси -> GetProxy
    check(ip='188.119.121.191', port=24531, model=model)

# db_check()
