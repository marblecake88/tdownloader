from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import pickle
import time
import traceback

# You need to click on second acceptall manually, thats the way
def remove_duplicate_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    unique_lines = sorted(set(lines))
    with open(file_path, 'w') as file:
        file.writelines(unique_lines)

# Функция для чтения параметров из файла
def read_parameters_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

# Настройка драйвера
service = Service('/Users/user/PycharmProjects/valentin/chromedriver')
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Вход на сайт и сохранение cookies
driver.get('https://parts.terex.com/search?Ntt=10.01.1105')
wait = WebDriverWait(driver, 30)
try:
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.pdynamicbutton a.call')))
    accept_button.click()
except Exception as e:
    print("Всплывающее окно не найдено или уже закрыто")
username_input = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-username')))
password_input = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-password|input')))
username_input.send_keys('your@email.com')
password_input.send_keys('qwerty12345')
login_button = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-submit')))
login_button.click()
time.sleep(30)
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# Загрузка сохраненных cookies
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# Чтение параметров из файла и поиск информации на сайте
parameters = read_parameters_from_file("ids.txt")
main_folder = '/Users/user/PycharmProjects/terexdownloader'
os.makedirs(main_folder, exist_ok=True)
error_log = os.path.join(main_folder, 'error_log.txt')
all_products_info = os.path.join(main_folder, 'id_url_list.txt')

for param in parameters:
    try:
        url = f'https://parts.terex.com/search?Ntt={param}'
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        product_links = soup.find_all('a', {'class': ['ProductResultImage', 'ProductResultName']})
        with open(all_products_info, 'a') as file:
            for link in product_links:
                href = link.get('href')
                if href:
                    full_url = f"https://parts.terex.com/{href}"
                    file.write(f'{param}, {full_url}\n')
    except Exception as e:
        with open(error_log, 'a') as file:
            file.write(f'Error for URL {url}: {e}\n')
            file.write(f'{traceback.format_exc()}\n')

driver.quit()
remove_duplicate_lines(all_products_info)
