from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep


# from webdriver_manager.chrome import ChromeDriverManager
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("headless")
# chrome_options.add_argument(r"user-data-dir=C:\Users\naits\AppData\Local\Google\Chrome\User Data")
# chrome_options.add_argument(r"--profile-directory=C:\Users\naits\AppData\Local\Google\Chrome\User Data\Default")
# chrome_options.debugger_address = "127.0.0.1:9222"
# browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

firefox_profile = webdriver.FirefoxProfile(
    r"C:\Users\juanb\AppData\Roaming\Mozilla\Firefox\Profiles\e5i6om3m.olympBotEURUSD")
firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = True  # Mostrar o no la página
""" profileOlympBot """
browser = webdriver.Firefox(firefox_profile=firefox_profile,
                            executable_path=GeckoDriverManager().install(), options=firefox_options)


browser.get("https://olymptrade.com")


def startBot():
    browser.refresh()
    print("Iniciando")
    # Rate of Retun
    elementos = []
    global span_rate, bottom_up, bottom_down, input_amount, input_duration, span_balance, btn_trading
    # 500 PANTALLA COMPELTA
    # 422 MEDIA PANTALLA
    # 413 CUARTO PANTALLA
    exists_rate = False
    exists_bottom_up = False
    exists_bottom_down = False
    exists_amount = False
    exists_duration = False
    exists_balance = False
    exists_trading = False
    noExists = True
    while noExists:  # 500 es el numero de elemntos total pero el ultimo boton que se necesita es de 386
        elementos = browser.find_elements(by=By.CSS_SELECTOR, value="*")
        if(len(elementos) > 400):
            for elemento in elementos:
                # print(elemento.get_attribute('data-test'))
                try:
                    dataSet = elemento.get_attribute('data-test')
                    exists_rate = False if dataSet == 'asset-select-button' else True
                    exists_bottom_up = False if dataSet == 'deal-button-up' else True
                    exists_bottom_down = False if dataSet == 'deal-button-down' else True
                    exists_amount = False if dataSet == 'deal-amount-input' else True
                    exists_duration = False if dataSet == 'deal-duration-input' else True
                    exists_balance = False if dataSet == 'balance' else True
                    exists_trading = False if dataSet == 'sidebar-btn-trading-bar' else True
                except:
                    continue
            noExists = not (
                exists_rate and exists_bottom_up and exists_bottom_down and exists_amount and exists_duration and exists_balance and exists_trading)
        print(len(elementos), noExists)
        sleep(1)

    print("Iniciado")
    for elemento in elementos:
        try:
            if(elemento.tag_name == 'button' or elemento.tag_name == 'input'):
                elem = elemento.get_attribute('data-test')
                if(elem == 'asset-select-button'):
                    span_rate = elemento
                if(elem == 'deal-button-up'):
                    bottom_up = elemento
                if(elem == 'deal-button-down'):
                    bottom_down = elemento
                if(elem == 'deal-amount-input'):
                    input_amount = elemento
                if(elem == 'deal-duration-input'):
                    input_duration = elemento
                if(elem == 'balance'):
                    span_balance = elemento
                if(elem == 'sidebar-btn-trading-bar'):
                    btn_trading = elemento
        except:
            continue


def clickUp(times=1):
    count = 1
    while count <= times:
        bottom_up.click()
        count = count+1


def clickDown(times=1):
    count = 1
    while count <= times:
        bottom_down.click()
        count = count+1


def clickTrading():
    btn_trading.click()


def getRate():
    return int(span_rate.text.replace('%', '').replace('EUR/USD', '').replace('OTC', ''))


def getAmount():
    return int(input_amount.get_attribute('value').replace('Đ', ''))


def getDuration():
    return input_duration.get_attribute('value')


def getBalance():
    return float(span_balance.text.replace('Đ', '').replace('.', '').replace(',', '').replace('DEMO ACCOUNT', '').replace('CUENTA DEMO', ''))


def setAmount(amount):
    input_amount.send_keys(Keys.HOME)
    input_amount.send_keys(Keys.DELETE)
    input_amount.send_keys(amount)
    input_amount.send_keys(Keys.RETURN)


def setDuration(duration):
    return int(input_duration.send_keys(duration))
