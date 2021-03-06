from database.DatabaseModel import ProxyModel
import requests
import re

class GetProxy:

    # прокси с базы данных
    def get_list():
        proxy_list = []
        proxies = ProxyModel.select().where(ProxyModel.status == 1)
        for proxy in proxies:
            proxy_list.append({
                'host': proxy.host,
                'port': proxy.port,
                'login': proxy.login,
                'password': proxy.password
            })

        return proxy_list


    # достаем прокси с nosok
    def get_from_url():

        proxy_list = []
        # ссылку на список прокси менять здесь
        res = requests.get('http://nosok.org/export?id=b321423a&type=1&format=proxy&ipField=ip_dynamic_with_replace').text

        with open('nosokproxy.txt', 'w') as file:
            file.write(res)
            
        with open('nosokproxy.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                host = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                port = re.findall(r':(\d{1,5})', line)
                proxy_list.append({
                    'host': host[0],
                    'port': port[0],
                    'login': '',
                    'password': ''
                })
        
        return proxy_list