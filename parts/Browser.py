from selenium import webdriver
from fake_useragent import UserAgent

class Browser:

    def my_browser(ip=None, port=None):

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

        options.headless = False

        browser = webdriver.Firefox(
            # for windows
            # executable_path="firefoxdriver\geckodriver.exe",

            # for linux
            executable_path='firefoxdriver/geckodriver',

            options=options,
        )
        browser.set_window_size(1272, 774)

        return browser

    @staticmethod
    def gen_cookie(cookie_list):
        cookie_str = ''
        for c in cookie_list:
            cookie_str = cookie_str + c['name'] + '=' + c['value'] + '; '

        return cookie_str
