from parts.Browser import Browser
from parts.GetProxy import GetProxy
from database.DatabaseModel import OrdersModel

import time
import json

# testing db conn
def db_check():
    all_info = OrdersModel.select().get()

    row_id = all_info.id
    OrdersModel.update_with_status_3(id=row_id)


def check(ip, port):

    browser = Browser.my_browser(ip, port)
    try:
  
        try:
            browser.get('https://www.farfetch.com/ua/useraccount.aspx')
            login_input = browser.find_element_by_id('email-input-login')
            login_input.send_keys('11mself@stmaryscalne.org')
            time.sleep(3)
            pass_input = browser.find_element_by_id('password-input-login')
            pass_input.send_keys('polo55')
            time.sleep(3)
            checkbox = browser.find_element_by_id('RememberMe')

            # метод click() приводит к ошибке при нажатии на чекбокс
            browser.execute_script("arguments[0].click();", checkbox) 
            time.sleep(3)

            # поиск по xpath, id или class не подходит
            login_btn = browser.find_element_by_xpath('/html/body/div[3]/main/section/div[2]/div/div/div[1]/div[1]/div/form/div[7]/button')
            login_btn.click()
            time.sleep(3)

            browser.get('https://www.farfetch.com/ua/addressbook/')
            # time.sleep(3)
            # address = json.loads(browser.find_element_by_id("json").text)
            # print(address)


            # browser.get('https://www.farfetch.com/ua/ajax/userdetails')
            # time.sleep(3)
            #
            # browser.get('https://www.farfetch.com/ua/orders/')
            # print(json.loads(browser.find_element_by_id("json").text))

            time.sleep(80)
        except Exception as expt:
            print(expt)
        
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


if __name__ == '__main__':
    # model = OrdersModel.get_by_email('Andrew.abraham@mac.com')
    # model.__setattr__('countryCode', 'ru_RU')
    # model.save()
    # i=0
    # ip, port = None. Для работы с прокси -> GetProxy
    check(ip='176.28.64.225', port=3128)

# db_check()
