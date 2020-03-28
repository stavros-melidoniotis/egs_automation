from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from apscheduler.schedulers.blocking import BlockingScheduler

import secrets
import platform
import os
import webbrowser
import time

TIMEOUT_IN_SECONDS = 30
EGS_URL = 'https://www.epicgames.com/id/login?productName=epic-games&lang=en_US&' \
          'redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fstore%2Fen-US%2Ffree-games&' \
          'client_id=5a6fcd3b82e04f8fa0065253835c5221&noHostRedirect=true'

LOGIN_FORM_XPATH = '//*[@id="root"]/div/div/div/div/div[2]/div/form'
SUBMIT_LOGIN_BUTTON_XPATH = '//*[@id="login"]'
GAMES_LIST_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[1]/div[4]/div[2]/div/div/section/div'
CONTINUE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[4]/div/div[2]/div/button'
PURCHASE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[2]/div[2]/div[3]/div' \
                        '/div/div[3]/div/button'
MULTIPLE_EDITIONS_PURCHASE_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[4]/div[2]' \
                                   '/div[2]/div[2]/div[2]/div/div[2]/div/button'
COOKIE_ACCEPT_XPATH = '//*[@id="euCookieAccept"]'
PLACE_ORDER_BUTTON_XPATH = '//*[@id="purchase-app"]/div/div[4]/div[1]/div[2]/div[5]/div/div/button'
INCORRECT_RESPONSE_XPATH = '//*[@id="root"]/div/div/div/div/div[2]/div/form/h6'
LOGIN_CAPTCHA_XPATH = '//*[@id="FunCAPTCHA"]'
GAME_CARD_CLASS = 'CardGrid-card_57b1694f'
MATURE_CONTENT_TEXT_CLASS = 'WarningTemplate-messageText_06273162'


def create_browser_driver(system, default_browser):
    path = os.getcwd() + '/browser_drivers/' + system
    print('System:', system, '\nDefault browser:', default_browser, '\nPath:', path)
    browser_driver = None

    if system == 'Linux':
        if default_browser == 'google-chrome':
            browser_driver = webdriver.Chrome(executable_path=path + '/chromedriver')
        elif default_browser == 'firefox':
            browser_driver = webdriver.Firefox(executable_path=path + '/geckodriver')
        elif default_browser == 'opera':
            browser_driver = webdriver.Opera(executable_path=path + '/operadriver')
    elif system == 'Windows':
        if default_browser == 'google-chrome':
            browser_driver = webdriver.Chrome(executable_path=path + '/chromedriver.exe')
        elif default_browser == 'firefox':
            browser_driver = webdriver.Firefox(executable_path=path + '/geckodriver.exe')
        elif default_browser == 'opera':
            browser_driver = webdriver.Opera(executable_path=path + '/operadriver.exe')

    return browser_driver


def wait_for_element(driver, element):
    WebDriverWait(driver, TIMEOUT_IN_SECONDS).until(EC.presence_of_element_located((By.XPATH, element)))


def login_with_user_credentials(driver):
    username_input = driver.find_element_by_xpath('//*[@id="usernameOrEmail"]')
    password_input = driver.find_element_by_xpath('//*[@id="password"]')
    submit_button = driver.find_element_by_xpath(SUBMIT_LOGIN_BUTTON_XPATH)

    username_input.send_keys(secrets.username)
    password_input.send_keys(secrets.password)

    WebDriverWait(driver, TIMEOUT_IN_SECONDS).until(EC.element_to_be_clickable((By.XPATH, SUBMIT_LOGIN_BUTTON_XPATH)))
    submit_button.click()

    return


if __name__ == '__main__':
    # repeater = BlockingScheduler()
    #
    # @repeater.scheduled_job('interval', days=7)
    def get_free_games():
        browser = create_browser_driver(platform.system(), webbrowser.get().name)

        if browser is None:
            print('Your system or default browser is not supported!')
            exit(1)

        browser.get(EGS_URL)

        # wait for login form to load
        wait_for_element(browser, LOGIN_FORM_XPATH)
        login_with_user_credentials(browser)

        # keep_in_loop = True
        #
        # while keep_in_loop:
        #     login_with_user_credentials(browser)
        #
        #     if browser.find_elements_by_xpath(INCORRECT_RESPONSE_XPATH) or browser.find_elements_by_xpath(
        #             LOGIN_CAPTCHA_XPATH):
        #         print('something detected')
        #         browser.refresh()
        #     else:
        #         keep_in_loop = False
        #         print('continuing')

        # wait for games list to load
        wait_for_element(browser, GAMES_LIST_XPATH)
        games_list = browser.find_element_by_xpath(GAMES_LIST_XPATH).find_elements_by_class_name(GAME_CARD_CLASS)

        for game in games_list:
            availability = game.find_element_by_tag_name('span').text

            # open a new tab for each free game
            if availability == 'FREE NOW':
                link = game.find_element_by_tag_name('a').get_attribute('href')
                browser.execute_script('window.open(\'' + link + '\');')

        original_tab = browser.current_window_handle
        new_games_acquired = []

        for tab in browser.window_handles:
            if tab == original_tab:
                browser.close()
            else:
                browser.switch_to.window(tab)

                print('\n------------', browser.title, '------------')

                # if mature content warning is present then press continue button
                if browser.find_elements_by_xpath(CONTINUE_BUTTON_XPATH):
                    print('- closing mature content warning')
                    wait_for_element(browser, CONTINUE_BUTTON_XPATH)
                    browser.find_element_by_xpath(CONTINUE_BUTTON_XPATH).click()

                wait_for_element(browser, PURCHASE_BUTTON_XPATH)
                purchase_button = browser.find_element_by_xpath(PURCHASE_BUTTON_XPATH)

                # accept cookies to avoid them overlapping purchase button
                browser.find_element_by_xpath(COOKIE_ACCEPT_XPATH).click()

                if purchase_button.find_element_by_tag_name('span').text == "SEE EDITIONS":
                    print('- multiple editions detected')
                    purchase_button.click()
                    browser.find_element_by_xpath(MULTIPLE_EDITIONS_PURCHASE_XPATH).click()
                else:
                    wait_for_element(browser, PURCHASE_BUTTON_XPATH)

                    if purchase_button.find_element_by_tag_name('span').text == 'OWNED':
                        print('- game already owned')
                        continue
                    else:
                        print('- purchasing game')
                        purchase_button.click()

                wait_for_element(browser, PLACE_ORDER_BUTTON_XPATH)
                browser.find_element_by_xpath(PLACE_ORDER_BUTTON_XPATH).click()
                time.sleep(5)
                new_games_acquired.append(browser.title)

        print('\n\nYou\'ve acquired', len(new_games_acquired), 'new game(s)!\n')
        for i in range(len(new_games_acquired)):
            print(i + 1,')', new_games_acquired[i])

        browser.quit()

    # repeater.start()
    get_free_games()
