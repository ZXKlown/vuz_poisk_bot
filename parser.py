#НАЧАЛО ПАРСИНГА ОПЦИЙ✅✅✅✅✅✅✅
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

chrome_install = ChromeDriverManager().install()
chromedriver_path = os.path.join(os.path.dirname(chrome_install), "chromedriver.exe")
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Загрузка данных
with open("vuz_data_full.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Сбор всех уникальных ссылок
unique_links = set()
for city, categories in data.items():
    for category, vuz_list in categories.items():
        for vuz in vuz_list:
            link = vuz.get("vuz_link_optoins")
            if link:
                unique_links.add(link)

# Функция парсинга опций
def parse_vuz_options(link):
    try:
        driver.get(link)
        vuz_option = driver.find_element(By.CLASS_NAME, 'vuzOpiton')
        vuz_option_content = vuz_option.get_attribute("outerHTML")
        lines = vuz_option_content.split('\n')
        options_dict = {
            lines[i].split(':')[0].strip(): ('✅' if 'vuzok' in lines[i + 2] else '❌')
            for i in range(len(lines) - 2)
            if ':' in lines[i]
        }
        return options_dict
    except (TimeoutException, NoSuchElementException):
        return {}

# Создаём словарь с результатами для всех уникальных ссылок
results_dict = {}
for link in unique_links:
    print(f"Парсим {link}...")
    results_dict[link] = parse_vuz_options(link)

# Применяем результаты обратно к данным и удаляем 'vuz_link_optoins'
for city, categories in data.items():
    for category, vuz_list in categories.items():
        for vuz in vuz_list:
            link = vuz.pop("vuz_link_optoins", None)  # Удаляем ссылку
            if link and link in results_dict:
                vuz["options_check"] = results_dict[link]

# Сохраняем обновлённый файл
with open("vuz_data_full.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

driver.quit()
#КОНЕЦ ПАРСИНГА ОПЦИЙ✅✅✅✅✅✅✅✅✅✅✅✅








#НАЧАЛО ПАРСИНГА ВУЗОВ✅✅✅✅✅✅✅
############################
# import json
# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
#
# # Настройка Selenium
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
#
# chrome_install = ChromeDriverManager().install()
# chromedriver_path = os.path.join(os.path.dirname(chrome_install), "chromedriver.exe")
# service = Service(chromedriver_path)
# driver = webdriver.Chrome(service=service, options=chrome_options)
#
# # Загрузка данных
# with open("cities_specializations1.json", "r", encoding="utf-8") as f:
#     cities_data = json.load(f)
#
# collected_data = {}
#
#
# def scrape_page():
#     vuz_list = []
#     vuz_elements = driver.find_elements(By.CLASS_NAME, "newItemVuz") + driver.find_elements(By.CLASS_NAME,
#                                                                                             "newItemVuzPremium")
#
#     for vuz in vuz_elements:
#         try:
#             title = vuz.find_element(By.CLASS_NAME, "itemVuzTitle").text.strip()
#             description_elements = vuz.find_elements(By.CLASS_NAME, "opisItemVV")
#             description = description_elements[-1].text.split("\n")[2].strip() if description_elements else "Нет данных"
#
#             info_blocks = vuz.find_elements(By.CLASS_NAME, "info")
#             cost = " ".join(info_blocks[0].text.split("\n")) if len(info_blocks) > 0 else "Нет данных"
#             budget = " ".join(info_blocks[1].text.split("\n")) if len(info_blocks) > 1 else "Нет данных"
#             paid = " ".join(info_blocks[2].text.split("\n")) if len(info_blocks) > 2 else "Нет данных"
#             vuz_link = f"https://www.google.com/search?q={title}"
#
#             image_url = vuz.find_element(By.CLASS_NAME, "vuzPrevImg").get_attribute("src") if vuz.find_elements(
#                 By.CLASS_NAME, "vuzPrevImg") else "Нет данных"
#
#             link_vuz_options = "Нет данных"
#             try:
#                 block = driver.find_element(By.CSS_SELECTOR, 'div.col-md-7.blockAfter')
#                 link_element = block.find_element(By.TAG_NAME, 'a')
#                 link_vuz_options = link_element.get_attribute('href')
#             except:
#                 pass
#
#             vuz_list.append({
#                 "title": title,
#                 "description": description,
#                 "cost": cost,
#                 "budget": budget,
#                 "paid": paid,
#                 "image_url": image_url,
#                 "vuz_link": vuz_link,
#                 "vuz_link_optoins": link_vuz_options
#             })
#         except Exception as e:
#             print(f"Ошибка при обработке вуза: {e}")
#
#     return vuz_list
#
#
# def go_to_next_page():
#     try:
#         next_page_arrow = driver.find_elements(By.XPATH, "//a[span[contains(text(), 'keyboard_arrow_right')]]")
#         if next_page_arrow:
#             driver.get(next_page_arrow[0].get_attribute("href"))
#             return True
#         return False
#     except Exception as e:
#         print(f"Ошибка при переходе на следующую страницу: {e}")
#         return False
#
#
# for city, specializations in cities_data.items():
#     print(f"\nГород: {city}")
#     collected_data[city] = {}
#
#     for spec_name, _, spec_url in specializations:
#         print(f"Направление: {spec_name}")
#         driver.get(spec_url)
#         collected_data[city][spec_name] = []
#
#         while True:
#             collected_data[city][spec_name].extend(scrape_page())
#             if not go_to_next_page():
#                 break
#
# with open("vuz_data_full.json", "w", encoding="utf-8") as f:
#     json.dump(collected_data, f, ensure_ascii=False, indent=4)
#
# print("\nГотово! Всё сохранено в vuz_data_full.json")
# driver.quit()

##########################КОНЕЦ ПАРСИНГА ВУЗОВ✅✅✅✅✅✅✅✅✅





# Название: Российский государственный социальный университет
# Описание:Бизнес-информатика, Государственное и муниципальное управление, Гостиничное дело, Дизайн и еще 43 направления
# Стоимость обучения: от 57400 ₽
# Бюджет: от 133 1044 мест
# Платное: от 125 6672 мест














# driver.get('https://vuzopedia.ru/')
# driver.implicitly_wait(5)
#
# # Открываем список городов
# driver.find_element(By.ID, 'newChoose').click()
# driver.find_element(By.CLASS_NAME, 'showMoreCity').click()
#
# # Собираем ссылки на города
# linkscities = [link.get_attribute('href') for link in driver.find_elements(By.CLASS_NAME, 'itemCityLeft a')]
#
# # Обрабатываем каждую ссылку
# city_links = {}
# try:
#     with open("cities_specializations.json", "r", encoding="utf-8") as f:
#         cities_specializations = json.load(f)
# except (FileNotFoundError, json.JSONDecodeError):
#     cities_specializations = {}
#
#
#
# for city, link in city_links.items():
#     driver.get(link)
# #    time.sleep()  # Даем странице 1 секунду на загрузку
#
#     elements = driver.find_elements(By.CLASS_NAME, "col-md-3")
#
#     for elem in elements:
#
#         a_tag = elem.find_element(By.TAG_NAME, "a")
#         specialization_link = a_tag.get_attribute("href")
#         title = elem.find_element(By.CLASS_NAME, "vuzItemTitle").text
#         count = elem.find_element(By.CLASS_NAME, "cyrCountVUz").text
#         cities_specializations.setdefault(city, []).append([title, count, specialization_link])
#
#
# with open("cities_specializations.json", "w", encoding="utf-8") as f:
#     json.dump(cities_specializations, f, ensure_ascii=False, indent=4)

# driver.get('https://vuzopedia.ru/region/city/95')
#
# vuz_elements = driver.find_elements(By.CLASS_NAME, "newItemVuz") + driver.find_elements(By.CLASS_NAME, "newItemVuzPremium")
# for index in range(len(vuz_elements)):
#     vuz = vuz_elements[index]
#     vuz_title = vuz.find_element(By.CLASS_NAME, "itemVuzTitle")
#
#     driver.execute_script("arguments[0].scrollIntoView(true);", vuz_title)
#
#     driver.execute_script("arguments[0].click();", vuz_title)
#
#     vuz_option = driver.find_element(By.CLASS_NAME, 'vuzOpiton')
#
#     vuz_option_content = vuz_option.get_attribute("outerHTML")
#
#     lst_vuz = list(map(lambda x: "✅" if x.split('"')[0] == "vuzok" else "❌", vuz_option_content.split("material-icons ")[1:]))
#
#     print(lst_vuz)
