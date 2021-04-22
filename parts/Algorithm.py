from .Browser import Browser

import requests
import time


class Algorithm:

    def check(ip, port, username, password, model, custom_logger):
        try:
            browser = Browser.my_browser(ip, port, username, password)
            try:
                # тайм-аут загрузки
                browser.set_page_load_timeout(60)
                custom_logger.info(f'= Farfetch Parser | Account {model.email} | With {ip}:{port} =')
                try:
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