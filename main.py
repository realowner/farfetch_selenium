from re import match
from parts.Browser import Browser
from parts.GetProxy import GetProxy
from parts.ArgParser import ArgsParser
from database.DatabaseModel import OrdersModel

import time
import requests
from itertools import cycle
from threading import Thread
import math
import logging


def check(ip, port, username, password, model, custom_logger):
    try:
        browser = Browser.my_browser(ip, port, username, password)
        try:
            browser.set_page_load_timeout(60)
            custom_logger.info(f'= Farfetch Parser | Account {model.email} | With {ip}:{port} =')
            try:
                # browser.get('https://www.myip.ru')
                # time.sleep(10)
                browser.get('https://www.farfetch.com/ua/useraccount.aspx')
                browser.find_element_by_id('login-signIn')
                custom_logger.info('page load - DONE')
                try:
                    login_input = browser.find_element_by_id('email-input-login')
                    login_input.send_keys(model.email)
                    time.sleep(3)
                    pass_input = browser.find_element_by_id('password-input-login')
                    pass_input.send_keys(model.password)
                    time.sleep(3)
                    checkbox = browser.find_element_by_id('RememberMe')

                    browser.execute_script("arguments[0].click();", checkbox) 
                    time.sleep(3)

                    login_btn = browser.find_element_by_xpath('/html/body/div[3]/main/section/div[2]/div/div/div[1]/div[1]/div/form/div[7]/button')
                    login_btn.click()
                    time.sleep(3)

                    try:
                        login_validation = browser.find_element_by_id('js-passwordValidationMessage').text
                        login_validation_find = True
                        if 'Пройдите капчу' in login_validation:
                            login_validation_couse = 'capcha'
                        else:
                            login_validation_couse = 'wrong email or password'
                    except:
                        login_validation_find = False

                    cookie = browser.get_cookies()
                    cookie_str = Browser.gen_cookie(cookie)
                    headers = {'cookie': cookie_str}

                    browser.find_element_by_id('accordion-account')
                    custom_logger.info('login - DONE')
                    try:
                        userdetails_request = requests.get('https://www.farfetch.com/ua/ajax/userdetails', headers=headers)
                        userdetails_request_result = userdetails_request.json()

                        if userdetails_request_result['userDetails']['phoneNumber'] is None:
                            phone = None
                            model_ph_update = 'phone field not updated'
                        else:
                            phone = userdetails_request_result['userDetails']['phoneNumber']
                            model_ph_update = model.set_phone(phone)

                        custom_logger.info(f'userdetails - DONE > {str(userdetails_request.status_code)} | {model_ph_update}')
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

                            custom_logger.info(f'adressbook - DONE > {str(adress_request.status_code)} | {model_cn_update}; {model_ph_update}')
                            try:
                                orders_request = requests.get('https://www.farfetch.com/ua/orders/', headers=headers)
                                orders_request_result = orders_request.json()
                                orders_count = len(orders_request_result['orders'])

                                model_or_update = model.set_orders(orders_count)
                                custom_logger.info(f'orders - DONE > {str(orders_request.status_code)} | {model_or_update}')
                                update_status = model.set_status(2)
                                custom_logger.info(f'= Account {model.email} - {update_status} =')
                                custom_logger.info('--------------------')
                                return True

                            except Exception as orders_ex:
                                update_status = model.set_status(3)
                                custom_logger.info(f'-> orders error | responce {str(orders_request.status_code)} | {update_status}')
                                custom_logger.info(orders_ex)
                                custom_logger.info('--------------------')
                                return True

                        except Exception as adress_ex:
                            update_status = model.set_status(3)
                            custom_logger.info(f'-> adressbook error | responce {str(adress_request.status_code)} | {update_status}')
                            custom_logger.info(adress_ex)
                            custom_logger.info('--------------------')
                            return True

                    except Exception as user_details_ex:
                        update_status = model.set_status(3)
                        custom_logger.info(f'-> user details error | responce {str(userdetails_request.status_code)} | {update_status}')
                        custom_logger.info(user_details_ex)
                        custom_logger.info('--------------------')
                        return True

                except Exception as login_load_ex:
                    if login_validation_find == True:
                        if login_validation_couse == 'capcha':
                            update_status = model.set_status(4)
                            to_return = False
                        else:
                            update_status = model.set_status(3)
                            to_return = True
                    else:
                        update_status = model.set_status(3)

                    custom_logger.info(f'-> login error, {login_validation_couse} | {update_status}')
                    custom_logger.info(login_load_ex)
                    custom_logger.info('--------------------')
                    return to_return

            except Exception as pg_load_ex:
                update_status = model.set_status(4)
                custom_logger.info(f'-> bad proxy or useragent | {update_status}')
                custom_logger.info(pg_load_ex)
                custom_logger.info('--------------------')
                return False
            
        except Exception as global_ex:
            update_status = model.set_status(4)
            custom_logger.info(f'-> global | {update_status}')
            custom_logger.info(global_ex)
            custom_logger.info('--------------------')
        finally:
            browser.close()
            browser.quit()
    except Exception as start_ex:
        update_status = model.set_status(4)
        custom_logger.info(f'-> failed to connect to proxy | {update_status}')
        custom_logger.info(start_ex)
        custom_logger.info('--------------------')
        return False


def main(custom_logger, proxy_slice, factor, limit=None):

    # выборка записей для обработки
    if factor == 1:
        data = OrdersModel.select().where(OrdersModel.status == 1).limit(int(limit))
    else:
        data = OrdersModel.select().where(OrdersModel.status == 1).limit(int(limit)).offset(int(limit)*factor)
    
    # подготовка прокси для цикла
    proxies = proxy_slice
    proxies_count = len(proxies)
    cycler = cycle(proxies)
    first_proxy = next(cycler)
    curr_proxy = first_proxy

    # начальные данные для цикла
    do_it = True
    loop = 0
    rows_done = 1
    done_with_status_4 = 0
    done_with_status_3_2 = 0

    # цикл обработки записей
    for row in data:
        proxy_elem = curr_proxy

        # проверка возращаемого рузультата
        if do_it is False:
            custom_logger.info(f'THR-{factor}: PROXY RETURNED CAPCHA')

            loop += 1
            if loop == proxies_count:
                custom_logger.info(f'THR-{factor}: FULL PROXY CYCLE. SLEEP...')
                time.sleep(600)
                loop = 0
                proxy_elem = first_proxy
            proxy_elem = next(cycler)
            curr_proxy = proxy_elem            

        custom_logger.info(f'THR-{factor}: USING PROXY WITHOUT CAPCHA {rows_done}/{len(data)}')
        custom_logger.info('--------------------')

        # do_it = check(ip=proxy_elem['host'], port=int(proxy_elem['port']), username=proxy_elem['login'], password=proxy_elem['password'], model=row, custom_logger=custom_logger)
        do_it = check(ip=proxy_elem['host'], port=int(proxy_elem['port']), username=None, password=None, model=row, custom_logger=custom_logger)

        if do_it is False:
            custom_logger.info(f'THR-{factor}: STATUS - 4')
            done_with_status_4 += 1
        else:
            custom_logger.info(f'THR-{factor}: STATUS - 3/2')
            done_with_status_3_2 += 1
        rows_done += 1

    custom_logger.info('----------------------------------------')
    custom_logger.info(f'== THR-{factor}: STATUS 4 - {done_with_status_4} | STATUS 3/2 - {done_with_status_3_2} ==')
    custom_logger.info('----------------------------------------')


def with_threads(thread_num, limit=None):
    
    # выбор источника прокси
    proxies = GetProxy.get_from_url()
    # proxies = GetProxy.get_list()
    
    # распределение записей и прокси между тредами
    how_many_proxy = math.floor(len(proxies)/thread_num)
    term = how_many_proxy
    thread_list = []
    if limit:
        rows_for_thread = int(limit / thread_num)
    else:
        all_rows = OrdersModel.select().where(OrdersModel.status == 1)
        rows_for_thread = int(len(all_rows) / thread_num)

    # циклы запуска и остановки тредов 
    iteration = 0
    for count in range(0, thread_num):

        # настройки логера
        logger = logging.getLogger(f'thread_{count+1}')
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f'logs/thread_{count+1}.log', mode='w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        thread = Thread(target=main, name=f'THREAD {count+1}', args=(logger, proxies[iteration:how_many_proxy], count+1, int(rows_for_thread),))
        thread_list.append(thread)
        thread.start()
        print(f'Thread {count+1} started')
        iteration += term
        how_many_proxy += term

    for thr in thread_list:
        thr.join()    
        print(f'{thr} joined')


if __name__ == '__main__':
    args = ArgsParser.parse()

    if args.threads_count and args.rows_count:
        print(f'Parsing {args.rows_count} rows with {args.threads_count} threads')
        confim = input("Continue? (y/anything):")
        if confim == 'y':
            start_time = time.time()

            with_threads(thread_num=args.threads_count, limit=args.rows_count)

            print(f'= RUNNING TIME {time.time()-start_time} =')
        else:
            print('Bye')

    elif args.threads_count or args.rows_count:
        if args.rows_count:
            print(f'Parsing {args.rows_count} rows with 1 threads')

            confim = input("Continue? (y/anything):")
            if confim == 'y':
                start_time = time.time()
                
                with_threads(thread_num=1, limit=args.rows_count)

                print(f'= RUNNING TIME {time.time()-start_time} =')
            else:
                print('Bye')
        elif args.threads_count:
            print(f'Parsing all rows with {args.threads_count} threads')

            confim = input("Continue? (y/anything):")
            if confim == 'y':
                start_time = time.time()
                
                with_threads(thread_num=args.threads_count, limit=None)

                print(f'= RUNNING TIME {time.time()-start_time} =')
            else:
                print('Bye')
    else:
        print(f'Parsing all rows with 1 threads')
        confim = input("Continue? (y/anything):")
        if confim == 'y':
            start_time = time.time()
            
            with_threads(thread_num=1, limit=None)

            print(f'= RUNNING TIME {time.time()-start_time} =')
        else:
            print('Bye')