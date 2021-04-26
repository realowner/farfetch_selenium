from re import match
from parts.GetProxy import GetProxy
from parts.ArgParser import ArgsParser
from parts.Algorithm import Algorithm
from database.DatabaseModel import OrdersModel

import time
from itertools import cycle
from threading import Thread
import math
import logging


global_logger = logging.getLogger('global')
global_logger.setLevel(logging.INFO)
global_file_handler = logging.FileHandler('logs/global.log', mode='w')
global_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_file_handler.setFormatter(global_formatter)
global_logger.addHandler(global_file_handler)


def main(custom_logger, proxy_slice, factor, limit=None):

    # выборка записей для обработки
    if factor == 1:
        data = OrdersModel.select().where(OrdersModel.status == 1).limit(int(limit)) # row status here
    else:
        data = OrdersModel.select().where(OrdersModel.status == 1).limit(int(limit)).offset(int(limit)*(factor - 1)) # row status here
    
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

        do_it = Algorithm.check(ip=proxy_elem['host'], port=int(proxy_elem['port']), username=proxy_elem['login'], password=proxy_elem['password'], model=row, custom_logger=custom_logger)
        # do_it = Algorithm.check(ip=proxy_elem['host'], port=int(proxy_elem['port']), username=None, password=None, model=row, custom_logger=custom_logger)

        if do_it is False:
            custom_logger.info(f'THR-{factor}: STATUS - 4')
            done_with_status_4 += 1
        else:
            custom_logger.info(f'THR-{factor}: STATUS - 3/2')
            done_with_status_3_2 += 1
        rows_done += 1

    custom_logger.info('------------------------------------------')
    custom_logger.info(f'== THR-{factor}: STATUS 4 - {done_with_status_4} | STATUS 3/2 - {done_with_status_3_2} ==')
    custom_logger.info('------------------------------------------')


def with_threads(thread_num, limit=None):
    
    # выбор источника прокси
    # proxies = GetProxy.get_from_url()
    proxies = GetProxy.get_list()
    
    # распределение записей и прокси между тредами
    how_many_proxy = math.floor(len(proxies)/thread_num)
    term = how_many_proxy
    thread_list = []
    if limit:
        rows_for_thread = int(limit / thread_num)
    else:
        all_rows = OrdersModel.select().where(OrdersModel.status == 1) # row status here
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

        # запуск треда
        thread = Thread(target=main, name=f'THREAD {count+1}', args=(logger, proxies[iteration:how_many_proxy], count+1, int(rows_for_thread),))
        thread_list.append(thread)
        thread.start()
        global_logger.info(f'Thread {count+1} started')

        iteration += term
        how_many_proxy += term

    # завершение треда по окончанию работы
    for thr in thread_list:
        thr.join()    
        global_logger.info(f'{thr} joined')

    return 'ALL THREADS JOINED'


if __name__ == '__main__':
    args = ArgsParser.parse()

    if args.threads_count and args.rows_count:
        global_logger.info(f'Parsing {args.rows_count} rows with {args.threads_count} threads')
        confim = input("Continue? (y/anything):")
        if confim == 'y':
            global_logger.info(f'=== SCRIPT LAUNCHED | DEBUGGING ===')
            start_time = time.time()

            global_logger.info(with_threads(thread_num=args.threads_count, limit=args.rows_count))
            
            global_logger.info(f'= RUNNING TIME {time.time()-start_time} =')
        else:
            print('Bye')

    elif args.threads_count or args.rows_count:
        if args.rows_count:
            global_logger.info(f'Parsing {args.rows_count} rows with 1 threads')

            confim = input("Continue? (y/anything):")
            if confim == 'y':
                global_logger.info(f'=== SCRIPT LAUNCHED | DEBUGGING ===')
                start_time = time.time()
                
                global_logger.info(with_threads(thread_num=1, limit=args.rows_count))

                global_logger.info(f'= RUNNING TIME {time.time()-start_time} =')
            else:
                print('Bye')
        elif args.threads_count:
            global_logger.info(f'=== SCRIPT LAUNCHED | ENDLESS LOOP ===')

            threads = args.threads_count

            while threads == args.threads_count:
                try:
                    available_rows = len(OrdersModel.select().where(OrdersModel.status == 1))
                    modulo = available_rows % threads
                    int_res = available_rows - modulo
                    try:
                        if available_rows == 0:
                            global_logger.info('No accounts available. Sleep 900s...')
                            time.sleep(900)
                        elif int_res < threads:
                            global_logger.info('Nnot enough accounts. Sleep 900s...')
                            time.sleep(900)
                        else:
                            global_logger.info(f'----------------------------------------------')
                            global_logger.info(f'PARSING AVAILABLE ROWS WITH {threads} THREADS')
                            start_time = time.time()

                            global_logger.info(with_threads(thread_num=threads, limit=int_res))

                            global_logger.info(f'= RUNNING TIME {time.time()-start_time} =')
                            global_logger.info(f'----------------------------------------------')
                    except:
                        global_logger.info('Error in preparatory condition. Script stoped :(')
                        break
                except:
                    global_logger.info('Failed to connect to DB. Script stoped :(')
                    break

            # global_logger.info(f'Parsing all rows with {args.threads_count} threads')

            # confim = input("Continue? (y/anything):")
            # if confim == 'y':
            #     global_logger.info(f'=== SCRIPT LAUNCHED | DEBUGGING ===')
            #     start_time = time.time()
                
            #     global_logger.info(with_threads(thread_num=args.threads_count, limit=None))

            #     global_logger.info(f'= RUNNING TIME {time.time()-start_time} =')
            # else:
            #     print('Bye')
    else:
        global_logger.info(f'=== SCRIPT LAUNCHED | ENDLESS LOOP ===')

        # confim = input("Run an endless loop? (y/anything):")
        # if confim == 'y':

        # глобальное количество потоков
        # thr_input = input('Enter the number of threads: ')
        threads = 10

        while threads == 10:
            try:
                available_rows = len(OrdersModel.select().where(OrdersModel.status == 1))
                modulo = available_rows % threads
                int_res = available_rows - modulo
                try:
                    if available_rows == 0:
                        global_logger.info('No accounts available. Sleep 900s...')
                        time.sleep(900)
                    elif int_res < threads:
                        global_logger.info('Nnot enough accounts. Sleep 900s...')
                        time.sleep(900)
                    else:
                        global_logger.info(f'----------------------------------------------')
                        global_logger.info(f'PARSING AVAILABLE ROWS WITH {threads} THREADS')
                        start_time = time.time()

                        global_logger.info(with_threads(thread_num=threads, limit=int_res))

                        global_logger.info(f'= RUNNING TIME {time.time()-start_time} =')
                        global_logger.info(f'----------------------------------------------')
                except:
                    global_logger.info('Error in preparatory condition. Script stoped :(')
                    break
            except:
                global_logger.info('Failed to connect to DB. Script stoped :(')
                break

        # else:
        #     print('Bye')