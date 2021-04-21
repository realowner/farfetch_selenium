from selenium import webdriver
# from seleniumwire import webdriver
from fake_useragent import UserAgent
from .WindowSize import WindowSize

class Browser:

    def my_browser(ip=None, port=None, username=None, password=None):

        useragent = UserAgent()

        options = webdriver.FirefoxOptions()
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('dom.webnotifications.enabled', False)
        options.set_preference('media.volume_scale', '0.0')
        options.set_preference('general.useragent.override', useragent.random)

        if ip and port:
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', ip)
            options.set_preference('network.proxy.http_port', port)
            options.set_preference('network.proxy.https', ip)
            options.set_preference('network.proxy.https_port', port)
            options.set_preference('network.proxy.ssl', ip)
            options.set_preference('network.proxy.ssl_port', port)

            if useragent and password:
                proptions = {
                    'proxy': {
                        'http': f'http://{username}:{password}@{ip}:{port}',
                        'https': f'https://{username}:{password}@{ip}:{port}'
                    }
                }
            else:
                proptions = None

        options.headless = True

        browser = webdriver.Firefox(
            # for windows
            # executable_path="firefoxdriver\geckodriver.exe",
            # for linux
            executable_path='firefoxdriver/geckodriver',
            options=options
            # seleniumwire_options=proptions,
        )
        window_size = WindowSize.get_size()
        browser.set_window_size(window_size['width'], window_size['height'])

        return browser

    @staticmethod
    def gen_cookie(cookie_list):
        cookie_str = ''
        for c in cookie_list:
            cookie_str = cookie_str + c['name'] + '=' + c['value'] + '; '

        return cookie_str