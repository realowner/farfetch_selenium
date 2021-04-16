from parts.Browser import Browser
from parts.GetProxy import GetProxy
from database.DatabaseModel import OrdersModel

import time
import requests

# testing
def test(ip, port, model):
    browser = Browser.my_browser(ip, port)
    browser.set_page_load_timeout(60)
    try:

        browser.get('https://www.myip.ru')
        
        time.sleep(20)

    except Exception as x:
        print(x)
    finally:
        browser.close()
        browser.quit()


def check(ip, port, model):
    browser = Browser.my_browser(ip, port)
    try:
        browser.set_page_load_timeout(60)
        print(f'= Farfetch Parser | Account {model.email} =')
        try:
            browser.get('https://www.farfetch.com/ua/useraccount.aspx')
            browser.find_element_by_id('login-signIn')
            print('page load - DONE')
            try:
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

                try:
                    browser.find_element_by_id('js-passwordValidationMessage')
                    wrong_email = True
                except:
                    wrong_email = False

                cookie = browser.get_cookies()
                cookie_str = Browser.gen_cookie(cookie)
                headers = {'cookie': cookie_str}

                browser.find_element_by_id('accordion-account')
                print('login - DONE')
                try:
                    userdetails_request = requests.get('https://www.farfetch.com/ua/ajax/userdetails', headers=headers)
                    userdetails_request_result = userdetails_request.json()

                    if userdetails_request_result['userDetails']['phoneNumber'] is None:
                        phone = None
                        model_ph_update = 'phone field not updated'
                    else:
                        phone = userdetails_request_result['userDetails']['phoneNumber']
                        model_ph_update = model.set_phone(phone)

                    print(f'userdetails - DONE > {str(userdetails_request.status_code)} | {model_ph_update}')
                    try:
                        adress_request = requests.get('https://www.farfetch.com/ua/addressbook/', headers=headers)
                        adress_request_result = adress_request.json()
                        if len(adress_request_result['addressBook']['addresses']) != 0:
                            country = adress_request_result['addressBook']['addresses'][0]['flatAddress']['country']['nativeName']
                            countryCode = adress_request_result['addressBook']['addresses'][0]['flatAddress']['country']['alpha2Code']
                            model_cn_update = model.set_country(country, countryCode)
                            if phone is None:
                                phone = adress_request_result['addressBook']['addresses'][0]['flatAddress'].get('phone', None)
                                model_ph_update = model.set_phone(phone)
                            else:
                                model_ph_update = 'phone field was updated earlier'
                        else:
                            model_cn_update = 'country fields not updated'

                        print(f'adressbook - DONE > {str(adress_request.status_code)} | {model_cn_update}; {model_ph_update}')
                        try:
                            orders_request = requests.get('https://www.farfetch.com/ua/orders/', headers=headers)
                            orders_request_result = orders_request.json()
                            orders_count = len(orders_request_result['orders'])

                            # в будузем для суммы стоимости всех заказов
                            # if orders_count != 0:
                            #     for order in orders_request['orders']:
                            #         order_path = order['orderNumber']
                            #         single_orders_request = requests.get('https://www.farfetch.com/ua/ajax/orders/orderDetails/index/' + order_path, headers=headers)
                            #         single_orders_request_result = single_orders_request.json()

                            model_or_update = model.set_orders(orders_count)
                            print(f'orders - DONE > {str(orders_request.status_code)} | {model_or_update}')
                            update_status = model.set_status(2)
                            print(f'= Account {model.email} - {update_status} =')
                            print('--------------------')

                        except Exception as orders_ex:
                            update_status = model.set_status(4)
                            print(f'-> orders error | responce {str(orders_request.status_code)} | {update_status}')
                            # print('-> orders error')
                            print(orders_ex)
                            print('--------------------')

                    except Exception as adress_ex:
                        update_status = model.set_status(4)
                        print(f'-> adressbook error | responce {str(adress_request.status_code)} | {update_status}')
                        # print('-> adressbook error')
                        print(adress_ex)
                        print('--------------------')

                except Exception as user_details_ex:
                    update_status = model.set_status(4)
                    print(f'-> user details error | responce {str(userdetails_request.status_code)} | {update_status}')
                    # print('-> user details error')
                    print(user_details_ex)
                    print('--------------------')

            except Exception as login_load_ex:
                if wrong_email == True:
                    update_status = model.set_status(4)
                else:
                    update_status = model.set_status(3)
                print(f'-> login error | {update_status}')
                print(login_load_ex)
                print('--------------------')

        except Exception as pg_load_ex:
            update_status = model.set_status(3)
            print(f'-> bad proxy or useragent | {update_status}')
            print(pg_load_ex)
            print('--------------------')
        
    except Exception as global_ex:
        update_status = model.set_status(3)
        print(f'-> global | {update_status}')
        print(global_ex)
        print('--------------------')
    finally:
        browser.close()
        browser.quit()


if __name__ == '__main__':
    model = OrdersModel.get_by_email('Anthonyroberts@me.com')

    # цикл по бд
    data = OrdersModel.select().where(OrdersModel.status != 2)
    for row in data:
        check(ip=None, port=None, model=row)
        # check(ip='188.119.121.191', port=24531, model=row)

    # ip, port = None. Для работы с прокси -> GetProxy
    # test(ip='188.119.121.191', port=24531, model=model)
    # check(ip='173.249.5.7', port=8080)
    # check(ip=None, port=None, model=model)
