from database.DatabaseModel import ProxyModel

class GetProxy:

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