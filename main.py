from parts.Browser import Browser
from parts.GetProxy import GetProxy
from database.DatabaseModel import OrdersModel

import time
import json
import requests

# testing db conn
def db_check():
    all_info = OrdersModel.select().get()

    row_id = all_info.id
    OrdersModel.update_with_status_3(id=row_id)


def check(ip, port, model):

    try:
        browser = Browser.my_browser(ip, port)
        browser.set_page_load_timeout(60)
        print('= Farfetch Parser =')  
        try:
            browser.get('https://www.farfetch.com/ua/useraccount.aspx')
            try:
                print('page load - DONE')
                login_input = browser.find_element_by_id('email-input-login')
                login_input.send_keys('Anthonyroberts@me.com')
                time.sleep(3)
                pass_input = browser.find_element_by_id('password-input-login')
                pass_input.send_keys('gateacre1')
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

                try:
                    print('login - DONE')                   
                    # get phone info here

                    userdetails_request = requests.get('https://www.farfetch.com/ua/ajax/userdetails', headers=headers)
                    userdetails_request_result = userdetails_request.json()

                    if userdetails_request_result['userDetails']['phoneNumber'] is None:
                        phone = None
                    else:
                        phone = userdetails_request_result['userDetails']['phoneNumber']

                    try:
                        print('userdetails - DONE > ' + str(userdetails_request.status_code))
                        # get country info here
                        
                        adress_request = requests.get('https://www.farfetch.com/ua/addressbook/', headers=headers)
                        adress_request_result = adress_request.json()
                        if len(adress_request_result['addressBook']['addresses']) != 0:
                            country = adress_request_result['addressBook']['addresses'][0]['flatAddress']['country']['name']
                            countryCode = adress_request_result['addressBook']['addresses'][0]['flatAddress']['country']['alpha2Code']

                        try:
                            print('adressbook - DONE > ' + str(adress_request.status_code))
                            # get order info here

                            orders_request = requests.get('https://www.farfetch.com/ua/ajax/orders', headers=headers)
                            orders_request_result = orders_request.json()
                            orders_count = len(orders_request['orders'])
                            # if orders_count != 0:
                            #     for order in orders_request['orders']:
                            #         order_path = order['orderNumber']
                            #         single_orders_request = requests.get('https://www.farfetch.com/ua/ajax/orders/orderDetails/index/' + order_path, headers=headers)
                            #         single_orders_request_result = single_orders_request.json()

                            model.update_with_status(
                                country=country,
                                countryCode=countryCode,
                                zipCode=None,
                                phone=phone,
                                orderPrices=None,
                                status=2,
                                orders=orders_count,
                                cards=None,
                                date_of_check=None
                            )
                            print('orders - DONE > ' + str(orders_request.status_code))

                        except Exception as orders_ex:
                            print('-> orders error')
                            print(orders_ex)
                            print('--------------------')

                    except Exception as adress_ex:
                        print('-> adressbook error')
                        print(adress_ex)
                        print('--------------------')

                except Exception as user_details_ex:
                    print('-> user details error')
                    print(user_details_ex)
                    print('--------------------')

            except Exception as login_load_ex:
                model.set_status(4)
                print('-> login error')
                print(login_load_ex)
                print('--------------------')

        except Exception as pg_load_ex:
            model.set_status(4)
            print('-> bad proxy or useragent')
            print(pg_load_ex)
            print('--------------------')
        
    except Exception as global_ex:
        model.set_status(4)
        print('-> global')
        print(global_ex)
        print('--------------------')
    finally:
        browser.close()
        browser.quit()


if __name__ == '__main__':
    # model = OrdersModel.get_by_email('Andrew.abraham@mac.com')
    # model.__setattr__('countryCode', 'ru_RU')
    # model.save()
    # i=0
    x = 0
    data = OrdersModel.select()
    for row in data:
        check(ip=None, port=None, model=row)

    # ip, port = None. Для работы с прокси -> GetProxy
    # check(ip='188.119.121.191', port=24531)
    # check(ip='173.249.5.7', port=8080)
    # check(ip=None, port=None)
