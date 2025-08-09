from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import random

# Логи
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("Запуск автотеста")

driver = webdriver.Chrome()
driver.maximize_window()

try:
    logging.info("Открываю сайт")
    driver.get("https://ceramostone.kz/")

    wait = WebDriverWait(driver, 60)

    # Кнопка "Войти"
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Войти"))).click()
    logging.info("Клик по 'Войти'")

    # Кнопка "Регистрация"
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Регистрация"))).click()
    logging.info("Клик по 'Регистрация'")

    # Генерация уникального номера телефона (11 цифр, начинается с 77)
    phone_number = "77" + "".join([str(random.randint(0, 9)) for _ in range(9)])
    logging.info(f"Сгенерирован номер: {phone_number}")

    # Заполняем поля
    def fill_field(label_text, value):
        field = wait.until(EC.presence_of_element_located((
            By.XPATH, f"//p[contains(text(), '{label_text}')]/following-sibling::input"
        )))
        field.clear()
        field.send_keys(value)
        logging.info(f"Поле '{label_text}' заполнено")

    fill_field("Имя", "Александр")
    fill_field("Фамилия", "Иванов")
    fill_field("Номер телефона", phone_number)
    fill_field("Пароль", "Qwerty123!")
    fill_field("Повторите пароль", "Qwerty123!")

    # Кнопка "Регистрация" (по span)
    reg_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//span[contains(text(), 'Регистрация') and contains(@class, 'login-button')]/parent::*"
    )))
    reg_button.click()
    logging.info("Клик по кнопке 'Регистрация'")

    input("Тест завершён. Нажми Enter, чтобы закрыть браузер...")

except Exception as e:
    logging.error(f"Ошибка: {e}")

finally:
    driver.quit()
    logging.info("Браузер закрыт")
