import logging
import os
import random
import tempfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== ЛОГИ =====
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

IS_CI = os.environ.get("GITHUB_ACTIONS") == "true"

def make_driver():
    opts = Options()
    # для GitHub Actions — headless/безопасные флаги
    if IS_CI:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    # уникальный профиль, чтобы не ловить конфликт user data dir
    opts.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    service = Service(ChromeDriverManager().install())
    driver_ = webdriver.Chrome(service=service, options=opts)
    if not IS_CI:
        driver_.maximize_window()
    return driver_

def generate_phone() -> str:
    # 11 цифр, начинается с 77
    return "77" + "".join(str(random.randint(0, 9)) for _ in range(9))

def fill_field(wait: WebDriverWait, label_text: str, value: str):
    # ищем input сразу после подписи <p>…</p>
    xpath = f"//p[contains(normalize-space(), '{label_text}')]/following-sibling::input"
    field = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # На случай, если нужно дождаться кликабельности
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    field.clear()
    field.send_keys(value)
    logging.info(f"Поле '{label_text}' заполнено")

def click_registration_final(wait: WebDriverWait, driver):
    # Кликаем по span «Регистрация» (тот, что снизу под полями)
    span_xpath = "//span[contains(@class,'login-button') and contains(normalize-space(),'Регистрация')]"
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, span_xpath)))
    # подстраховка — скролл к кнопке
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    btn.click()
    logging.info("Клик по финальной кнопке 'Регистрация'")

def main():
    logging.info("Запуск автотеста")
    driver = make_driver()
    wait = WebDriverWait(driver, 60)

    try:
        logging.info("Открываю сайт")
        driver.get("https://ceramostone.kz/")

        # Войти
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Войти"))).click()
        logging.info("Клик по 'Войти'")

        # Регистрация
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Регистрация"))).click()
        logging.info("Клик по 'Регистрация'")

        # Заполняем поля
        fill_field(wait, "Имя", "Александр")
        fill_field(wait, "Фамилия", "Иванов")
        fill_field(wait, "Номер телефона", generate_phone())
        fill_field(wait, "Пароль", "Qwerty123!")
        fill_field(wait, "Повторите пароль", "Qwerty123!")

        # Финальная кнопка
        click_registration_final(wait, driver)

        logging.info("✅ Тест выполнен: форма отправлена (проверь результат на странице).")

        if not IS_CI:
            input("Тест завершён. Нажми Enter, чтобы закрыть браузер...")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        # В CI выводим ошибку в консоль, чтобы шаг пометился как failed
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        driver.quit()
        logging.info("Браузер закрыт")

if __name__ == "__main__":
    main()
