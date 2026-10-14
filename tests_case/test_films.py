import json
import os

import allure
import pytest
from dotenv import load_dotenv

from kinopoisk_api import KinopoiskAPI

load_dotenv()
API_KEY = os.getenv("KINOPOISK_API_KEY")

# Задаем верхнеуровневую группировку для всех тестов в этом файле
pytestmark = [allure.feature("Тестирование публичного неофициального API v1 / v2.2")]

@pytest.fixture(scope="module")
def api():
    """Инициализируем единый клиент Кинопоиска."""
    if not API_KEY:
        pytest.fail("Критическая ошибка: KINOPOISK_API_KEY не найден в переменных окружения или файле .env!")
        
    return KinopoiskAPI(api_key=API_KEY)

# ==========================================
# БЛОК 1: ТЕСТЫ ЭНДПОИНТОВ ФИЛЬМОВ И ДАННЫХ
# ==========================================

@allure.epic("Поиск фильма")
@allure.story("Получение детальной информации о фильме")
@allure.title("Успешное получение фильма по валидному ID")
@allure.description("Тест проверяет корректность статус-кода 200 и сверяет ключевые поля ответа API.")
@allure.severity(allure.severity_level.BLOCKER)
def test_get_film_details(api):
    film_id = 1402937
    
    with allure.step(f"Отправка GET-запроса для фильма ID: {film_id}"):
        response = api.films.get_by_id(film_id)
        
    with allure.step("Проверка статус-кода ответа (Ожидается 200)"):
        assert response.status_code == 200
        
    with allure.step("Валидация названия фильма в теле JSON"):
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=4), "Response JSON", allure.attachment_type.JSON)
        assert data["nameRu"] == "Артур, ты король"

@allure.epic("Поиск фильма")
@allure.story("Получение детальной информации о фильме")
@allure.title("Негативный тест: запрос фильма по несуществующему ID")
@allure.severity(allure.severity_level.MINOR)
def test_negativ_get_film_details(api):
    invalid_id = 8767773
    
    with allure.step(f"Отправка запроса с несуществующим ID: {invalid_id}"):
        response = api.films.get_by_id(invalid_id)
        
    with allure.step("Проверка статус-кода ошибки (Ожидается 404)"):
        assert response.status_code == 404

@allure.epic("Поиск фильма")
@allure.story("Поиск и фильтрация фильмов")
@allure.title("Получение топа фильмов (Категория TOP_250_BEST_FILMS)")
def test_get_top_films(api):
    with allure.step("Запрос первой страницы топа 250 лучших фильмов"):
        response = api.films.get_top(type_="TOP_250_BEST_FILMS", page=1)
        
    with allure.step("Проверка статус-кода и наличия ключа 'films'"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Top Films List", allure.attachment_type.JSON)
        assert "films" in data

@allure.epic("Поиск фильма")
@allure.story("Поиск и фильтрация фильмов")
@allure.title("Поиск фильма по ключевым словам")
def test_film_search_by_keyword(api):
    keyword_to_search = "Власть пса"
    
    with allure.step(f"Отправка поискового запроса по слову: '{keyword_to_search}'"):
        # Исправлено: убраны фигурные скобки, передаем чистую строку
        response = api.films_one.get_film_search_by_keyword(keyword_to_search, 1)
        
    with allure.step("Валидация результатов поиска"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Search Result JSON", allure.attachment_type.JSON)
        
        clean_keyword = data["keyword"].strip("'\"")
        assert "films" in data
        assert isinstance(data["films"], list)
        assert len(data["films"]) > 0, "Список найденных фильмов пуст"
        assert clean_keyword == keyword_to_search
        assert "pagesCount" in data


# ==========================================
# БЛОК 2: ФИНАНСЫ, КОЛЛЕКЦИИ И НАГРАДЫ
# ==========================================
@allure.epic("Глобальный поиск контента по фильтру")
@allure.story("Финансы и кассовые сборы")
@allure.title("Получение данных о бюджете и сборах фильма")
def test_get_box_office(api):
    film_id = 6750360   
    
    with allure.step(f"Запрос кассовых сборов для фильма ID: {film_id}"):       
        response = api.films.get_box_office(film_id)
        
    with allure.step("Базовая проверка структуры финансового ответа"):
        assert response.status_code == 200, f"Получен статус {response.status_code}"
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Box Office JSON", allure.attachment_type.JSON)
        assert "total" in data
        assert "items" in data
    
    with allure.step("Проверка валидности полей в списке сборов (если элементы есть)"):
        if len(data["items"]) > 0:
            # Защита от IndexError: безопасно проверяем доступность индекса или берем первый элемент
            index = 3 if len(data["items"]) > 3 else 0
            target_box = data["items"][index]
            assert "type" in target_box, "Отсутствует тип финансовой категории"
            assert "amount" in target_box, "Отсутствует сумма"

@allure.epic("Глобальный поиск контента по фильтру")
@allure.story("Награды и номинации")
@allure.title("Проверка наград фильма по его ID")
def test_films_awards(api):
    id_film = 1262931
    
    with allure.step(f"Запрос списка наград фильма ID: {id_film}"):
        response = api.films.get_awards(id_film)
        
    with allure.step("Проверка структуры и данных первой награды"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Awards JSON", allure.attachment_type.JSON)
        
        assert "items" in data and isinstance(data["items"], list)
        if len(data["items"]) > 0:
            assert data["items"][0]["name"] == "Золотой глобус"
            assert data["items"][0]["year"] == 2022

@allure.epic("Глобальный поиск контента по фильтру")
@allure.story("Списки и тематические коллекции")
@allure.title("Получение списка фильмов из коллекции (TOP_250_MOVIES)")
def test_get_collections(api):
    collection_type = "TOP_250_MOVIES"
    
    with allure.step(f"Запрос фильмов из коллекции: {collection_type}"):
        response = api.films.get_collections(collection_type, page=1)
        
    with allure.step("Проверяем лимиты пагинации (не более 20 фильмов на страницу)"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Actor Details JSON", allure.attachment_type.JSON)
        current_page_count = len(data["items"])
        assert 20 >= current_page_count > 0, f"Найдено фильмов: {current_page_count}, ожидалось <= 20"


# ==========================================
# БЛОК 3: СПРАВОЧНИКИ, ЖАНРЫ И ДРУГИЕ СЕРВИСЫ
# ==========================================

@allure.epic("Взаимодействия с каталогом фильмов")
@allure.story("Вспомогательные справочники API")
@allure.title("Запрос фильтров: валидация ID конкретных стран и жанров")
def test_gef_filters(api):
    with allure.step("Запрос конфигурационных фильтров стран и жанров"):
        response = api.films.gef_filters()
        
    with allure.step("Валидация справочника жанров (поиск ID: 3)"):
        assert response.status_code == 200
        data = response.json()
        genres_list = data["genres"]
        target_genre = next((item["genre"] for item in genres_list if item["id"] == 3), None)
        assert target_genre == "криминал"  
        
    with allure.step("Валидация справочника стран (поиск ID: 34)"):
        countries_list = data["countries"]
        target_countries = next((item["country"] for item in countries_list if item["id"] == 34), None)
        assert target_countries == "Россия"

@allure.epic("Взаимодействия с каталогом фильмов")
@allure.story("Поиск и фильтрация фильмов")
@allure.title("Запрос списка фильмов по конкретному жанру")
def test_get_films_genres(api):
    genre_id = 3
    with allure.step(f"Запрос фильмов, отфильтрованных по ID жанра: {genre_id}"):
        response = api.films.get_films_genres(genre_id) 
    with allure.step("Проверка доступности эндпоинта"):
        assert response.status_code == 200

@allure.epic("Взаимодействия с каталогом фильмов")
@allure.story("Сотрудники и актеры кино")
@allure.title("Поиск информации о персоне по её персональному ID")
def test_get_actor_info(api):
    actor_id = 24100
    with allure.step(f"Запрос информации об актере/персоне с ID: {actor_id}"):
        response = api.staff.get_staff_by_id(actor_id)
        
    with allure.step("Проверка успешности ответа и присутствия человека в списке"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Actor Details JSON", allure.attachment_type.JSON)
        assert "Джесси Ибарра" in data.values()

@allure.epic("Получение медиа контента")
@allure.story("Медиа-новости сайта")
@allure.title("Успешное получение ленты медиа-новостей")
@allure.severity(allure.severity_level.NORMAL)
def test_get_media_posts(api):
    with allure.step("Отправка запроса на получение первой страницы медиа-новостей"):
        response = api.media.get_media_posts(page=1)
        
    with allure.step("Проверка наполненности блока новостных постов"):
        assert response.status_code == 200
        data = response.json()
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), "Media Posts JSON", allure.attachment_type.JSON)
        current_page_count = len(data["items"])
        assert current_page_count > 0

    
    
    
    
     