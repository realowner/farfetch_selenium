from selenium import webdriver
from fake_useragent import UserAgent

class Browser:

    def my_browser(ip=None, port=None, username=None, password=None):

        useragent = UserAgent()

        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={useragent.random}')
        options.add_argument(f'--proxy-server={ip}:{port}')
        # options.set_headless(headless=True)

        options.headless = True

        browser = webdriver.Chrome(
            executable_path='chromedriver/chromedriver',
        )
        browser.set_window_size(1272, 774)

        return browser

    # @staticmethod
    def gen_cookie(cookie_list):
        cookie_str = ''
        for c in cookie_list:
            cookie_str = cookie_str + c['name'] + '=' + c['value'] + '; '

        return cookie_str