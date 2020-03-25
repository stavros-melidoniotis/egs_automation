from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import secrets

TIMEOUT_IN_SECONDS = 15

LOGIN_FORM_XPATH = '//*[@id="root"]/div/div/div/div/div[2]/div/form'
SUBMIT_LOGIN_BUTTON_XPATH = '//*[@id="login"]'
GAMES_LIST_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[1]/div[4]/div[2]/div/div/section/div'
CONTINUE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[4]/div/div[2]/div/button'
PURCHASE_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[2]/div[2]/div[3]/div/div/div[3]/div/button'
SEE_EDITIONS_BUTTON_XPATH = '//*[@id="dieselReactWrapper"]/div/div[4]/div[3]/div/div[2]/div[4]/div/div/div[3]/div/button'

GAME_CARD_CLASS = 'CardGrid-card_57b1694f'
MATURE_CONTENT_TEXT_CLASS = 'WarningTemplate-messageText_06273162'


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
    browser = webdriver.Chrome('/home/stavr/Downloads/chromedriver')
    browser.get('https://www.epicgames.com/id/login?productName=epic-games&lang=en_US&'
                'redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fstore%2Fen-US%2Ffree-games&'
                'client_id=5a6fcd3b82e04f8fa0065253835c5221&noHostRedirect=true')

    # wait for login form to load
    WebDriverWait(browser, TIMEOUT_IN_SECONDS).until(EC.presence_of_element_located((By.XPATH, LOGIN_FORM_XPATH)))

    login_with_user_credentials(browser)

    # wait for games list to load
    WebDriverWait(browser, TIMEOUT_IN_SECONDS).until(EC.presence_of_element_located((By.XPATH, GAMES_LIST_XPATH)))

    games_list = browser.find_element_by_xpath(GAMES_LIST_XPATH).find_elements_by_class_name(GAME_CARD_CLASS)
    original_tab = browser.current_window_handle

    for game in games_list:
        availability = game.find_element_by_tag_name('span').text

        if availability == 'FREE NOW':
            link = game.find_element_by_tag_name('a').get_attribute('href')
            browser.execute_script('window.open(\'' + link + '\');')

    # loop through open tabs
    for tab in browser.window_handles:
        if tab != original_tab:
            print(tab)
            browser.switch_to.window(tab)

            # if mature content warning is present then press continue button
            if EC.presence_of_element_located((By.CLASS_NAME, MATURE_CONTENT_TEXT_CLASS)):
                print('Closing mature warning on tab', tab)
                browser.find_element_by_xpath(CONTINUE_BUTTON_XPATH).click()

            # WebDriverWait(browser, TIMEOUT_IN_SECONDS).until(EC.presence_of_element_located((By.XPATH, PURCHASE_BUTTON_XPATH)))

            # check if game has multiple editions
            # if EC.presence_of_element_located((By.XPATH, SEE_EDITIONS_BUTTON_XPATH)):
            #     WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, SEE_EDITIONS_BUTTON_XPATH)))
            #     browser.find_element_by_xpath(SEE_EDITIONS_BUTTON_XPATH).click()
            # else:
            WebDriverWait(browser, TIMEOUT_IN_SECONDS).until(EC.element_to_be_clickable((By.XPATH, PURCHASE_BUTTON_XPATH)))
            browser.find_element_by_xpath(PURCHASE_BUTTON_XPATH).click()

            # browser.close()

