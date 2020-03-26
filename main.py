from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import secrets
import platform
import os
import webbrowser

TIMEOUT_IN_SECONDS = 15

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

GAME_CARD_CLASS = 'CardGrid-card_57b1694f'
MATURE_CONTENT_TEXT_CLASS = 'WarningTemplate-messageText_06273162'


def detect_user_preferred_browser(os_name):
    user_preferred_browser = webbrowser.get(using=None).name
    print('OS:', os_name, '\nBrowser:', user_preferred_browser)
    path = os.getcwd() + '/browser_drivers/' + os_name

    if user_preferred_browser == 'google-chrome':
        default_browser = webdriver.Chrome(path + '/chromedriver')
    elif user_preferred_browser == 'firefox':
        default_browser = webdriver.Firefox(path + '/geckodriver')
    elif user_preferred_browser == 'opera':
        default_browser = webdriver.Opera(path + '/chromedriver')
    elif user_preferred_browser == 'safari':
        default_browser = webdriver.Safari(path)
    elif user_preferred_browser == 'windows-default':
        default_browser = webdriver.Edge(path)
    else:
        print('No browser found!')

    return default_browser


def login_with_user_credentials(driver, wait):
    username_input = driver.find_element_by_xpath('//*[@id="usernameOrEmail"]')
    password_input = driver.find_element_by_xpath('//*[@id="password"]')
    submit_button = driver.find_element_by_xpath(SUBMIT_LOGIN_BUTTON_XPATH)

    username_input.send_keys(secrets.username)
    password_input.send_keys(secrets.password)

    wait.until(EC.element_to_be_clickable((By.XPATH, SUBMIT_LOGIN_BUTTON_XPATH)))
    submit_button.click()

    return


if __name__ == '__main__':
    system = platform.system()

    if system == 'Linux':
        browser = detect_user_preferred_browser('linux')
    elif system == 'Windows':
        browser = detect_user_preferred_browser('windows')
    elif system == 'Darwin':
        browser = detect_user_preferred_browser('ios')

    browser.get(EGS_URL)
    wait = WebDriverWait(browser, TIMEOUT_IN_SECONDS)

    # wait for login form to load
    wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_FORM_XPATH)))

    login_with_user_credentials(browser, wait)

    # wait for games list to load
    wait.until(EC.presence_of_element_located((By.XPATH, GAMES_LIST_XPATH)))

    games_list = browser.find_element_by_xpath(GAMES_LIST_XPATH).find_elements_by_class_name(GAME_CARD_CLASS)
    original_tab = browser.current_window_handle

    for game in games_list:
        availability = game.find_element_by_tag_name('span').text

        if availability == 'FREE NOW':
            link = game.find_element_by_tag_name('a').get_attribute('href')
            browser.execute_script('window.open(\'' + link + '\');')

    cookies_accepted = False

    # loop through open tabs
    for tab in browser.window_handles:
        if tab == original_tab:
            browser.close()
        else:
            browser.switch_to.window(tab)

            # if mature content warning is present then press continue button
            if len(browser.find_elements_by_xpath(CONTINUE_BUTTON_XPATH)) > 0:
                print('Closing mature warning on tab', browser.title)
                browser.find_element_by_xpath(CONTINUE_BUTTON_XPATH).click()

            wait.until(EC.presence_of_element_located((By.XPATH, PURCHASE_BUTTON_XPATH)))
            purchase_button = browser.find_element_by_xpath(PURCHASE_BUTTON_XPATH)
            browser.find_element_by_xpath(COOKIE_ACCEPT_XPATH).click()

            if purchase_button.find_element_by_tag_name('span').text == "SEE EDITIONS":
                print('Multiple editions detected on', browser.title)
                purchase_button.click()
                browser.find_element_by_xpath(MULTIPLE_EDITIONS_PURCHASE_XPATH).click()
            else:
                print('Pressing purchase button on', browser.title)

                if purchase_button.find_element_by_tag_name('span').text == 'OWNED':
                    print('Game already owned on', browser.title)
                    continue
                else:
                    purchase_button.click()

            wait.until((EC.presence_of_element_located((By.XPATH, PLACE_ORDER_BUTTON_XPATH))))
            browser.find_element_by_xpath(PLACE_ORDER_BUTTON_XPATH).click()
            break
