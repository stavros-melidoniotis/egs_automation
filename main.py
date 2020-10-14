from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import secrets
import platform
import os
import time

TIMEOUT_IN_SECONDS = 30
EGS_URL = 'https://www.epicgames.com/id/login?lang=en_US&redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fstore%2Fen-US%2F&client_id=875a3b57d3a640a6b7f9b4e883463ab4&noHostRedirect=true'

SIGN_IN_WITH_EPIC_GAMES_XPATH = '//*[@id="login-with-epic"]'
LOGIN_FORM_XPATH = '//*[@id="root"]/div/div/div/div/div[2]/div/form'
USERNAME_XPATH = '//*[@id="email"]'
PASSWORD_XPATH = '//*[@id="password"]'
LOGIN_BUTTON_XPATH = '//*[@id="login"]'

GAMES_LIST_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[1]/div[4]/div[2]/div/div/section/div'
CONTINUE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[4]/div/div[2]/div/button'
PURCHASE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[2]/div[2]/div[3]/div/div/div[3]/div/button'
MULTIPLE_EDITIONS_PURCHASE_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[4]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/button'
COOKIE_ACCEPT_XPATH = '//*[@id="euCookieAccept"]'
PLACE_ORDER_BUTTON_XPATH = '//*[@id="purchase-app"]/div/div[4]/div[1]/div[2]/div[5]/div/div/button'
INCORRECT_RESPONSE_XPATH = '//*[@id="root"]/div/div/div/div/div[2]/div/form/h6'
LOGIN_CAPTCHA_XPATH = '//*[@id="FunCAPTCHA"]'
GAME_CARD_CLASS = 'CardGrid-card_57b1694f'
MATURE_CONTENT_TEXT_CLASS = 'WarningTemplate-messageText_06273162'


def create_browser_driver(system):
    linux_path = os.getcwd() + '/browser_drivers/' + system
    windows_path = os.getcwd() + '\\browser_drivers\\' + system
    browser_driver = None

    if system == 'Linux':
        browser_driver = webdriver.Chrome(executable_path=linux_path + '/chromedriver')
    elif system == 'Windows':
        browser_driver = webdriver.Chrome(executable_path=windows_path + '\chromedriver.exe')

    return browser_driver


def wait_for_element(driver, element):
    WebDriverWait(driver, TIMEOUT_IN_SECONDS).until(EC.presence_of_element_located((By.XPATH, element)))


if __name__ == '__main__':
    browser = create_browser_driver(platform.system())
    browser.get(EGS_URL)

    wait_for_element(browser, SIGN_IN_WITH_EPIC_GAMES_XPATH)

    browser.find_element_by_xpath(SIGN_IN_WITH_EPIC_GAMES_XPATH).click()

    wait_for_element(browser, LOGIN_FORM_XPATH)
    browser.find_element_by_xpath(USERNAME_XPATH).send_keys(secrets.username)
    browser.find_element_by_xpath(PASSWORD_XPATH).send_keys(secrets.password)
    login_button = browser.find_element_by_xpath(LOGIN_BUTTON_XPATH)

    WebDriverWait(browser, TIMEOUT_IN_SECONDS).until(EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH)))
    login_button.click()

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

            print('\n------------ {} ------------'.format(browser.title))

            # if mature content warning is present press continue button
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
