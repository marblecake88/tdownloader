from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import time
import pickle
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def clean_image_url(img_url):
    # Удаление лишних параметров из URL изображения
    return img_url.split('&')[0]

def download_image(url, folder, name):
    # Скачивание изображения и сохранение в указанной папке
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder, name), 'wb') as file:
            file.write(response.content)

# Настройка драйвера
service = Service('/Users/user/PycharmProjects/valentin/chromedriver')
chrome_options = Options()

# chrome_options.add_argument("--headless") # Раскомментируйте для безголового режима
driver = webdriver.Chrome(service=service, options=chrome_options)

# Вход на сайт
driver.get('https://parts.terex.com/search?Ntt=10.01.1105')
wait = WebDriverWait(driver, 30)

# Закрытие всплывающего окна, если оно есть
try:
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.pdynamicbutton a.call')))
    accept_button.click()
except Exception as e:
    print("Всплывающее окно не найдено или уже закрыто")

# Ожидание загрузки элементов формы входа
username_input = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-username')))
password_input = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-password|input')))
username_input.send_keys('your@email.com')
password_input.send_keys('qwerty666')

# Использование JavaScript для клика по кнопке входа, если обычный клик не работает
login_button = wait.until(EC.presence_of_element_located((By.ID, 'idcs-signin-basic-signin-form-submit')))
driver.execute_script("arguments[0].click();", login_button)

# Ожидание для завершения процесса входа
time.sleep(30)

# Сохранение cookies после входа
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# Чтение URL-адресов из файла
with open('urls.txt', 'r') as file:
    urls = file.readlines()

# Обработка каждого URL
for url in urls:
    driver.get(url.strip())

    # Ждем, пока страница загрузится
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_name = soup.select_one('.ProductName').get_text(strip=True)
    part_number = soup.select_one('.PartNumber').get_text(strip=True)

    folder_name = part_number
    os.makedirs(folder_name, exist_ok=True)

    images = soup.select('img[srcset]')
    for i, img in enumerate(images):
        srcset = img.get('srcset', '').split(',')
        image_url = clean_image_url(srcset[-1].split()[0])  # Выбор наибольшего доступного изображения
        full_image_url = urljoin(url, image_url)  # Создание полного URL изображения
        download_image(full_image_url, folder_name, f'image_{i}.jpg')

    with open(os.path.join(folder_name, 'product_info.txt'), 'w') as file:
        file.write(f'Name: {product_name}\nPart Number: {part_number}\n')

driver.quit()
