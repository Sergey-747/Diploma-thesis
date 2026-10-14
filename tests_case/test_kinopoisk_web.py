import os
import unittest

import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Pages import AuthProfilesPage, MainPage, MoviePage, SearchResultsPage, Top250Page

LocatorType = tuple[str, str]

class KinopoiskUITests(unittest.TestCase):
    def setUp(self):
        """Настройка браузера перед каждым тестом"""
        chrome_options = Options()
        user_data_dir = os.path.join(os.getcwd(), "selenium_chrome_profile")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(60)

        # Инициализируем страницы
        self.main_page = MainPage(self.driver)
        self.search_results_page = SearchResultsPage(self.driver)
        self.top250_page = Top250Page(self.driver)
        self.movie_page = MoviePage(self.driver)
        self.auth_profiles_page = AuthProfilesPage(self.driver)

    def tearDown(self):
        """Закрытие браузера после каждого теста"""
        if self.driver:
            self.driver.quit()

    @allure.epic("Глобальный поиск контента")
    @allure.feature("Поиск по названию")
    @allure.story("Успешный поиск фильма по точному имени")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_movie_by_name(self):
        """Тест-кейс №1: Поиск фильма по точному названию"""
        with allure.step("Открыть главную страницу Кинопоиска"):
            self.main_page.open()

        with allure.step("Ввести в поиск 'Интерстеллар' и нажать Enter"):
            self.main_page.search_for("Интерстеллар")

        with allure.step("Проверить, что первый результат содержит 'Интерстеллар'"):
            result_text = self.search_results_page.get_first_result_text()
            self.assertIn("Интерстеллар", result_text)

    @allure.epic("Глобальный поиск контента")
    @allure.feature("Поиск по имени актера")
    @allure.story("Успешный поиск фильмографии актёра")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_actor_by_name(self):
        """Тест-кейс №2: Поиск по имени актера"""
        with allure.step("Открыть главную страницу Кинопоиска"):
            self.main_page.open()

        with allure.step("Поиск по фамилии актера"):
            self.main_page.search_for("Леонардо Ди Каприо")

        with allure.step("Проверяем, что результат содержит 'Леонардо ДиКаприо'"):
            actor_text = self.search_results_page.get_actor_heading_text()
        self.assertIn("Леонардо ДиКаприо", actor_text)
        print(
            f"[ASSERT] Проверка прошла успешно. Актёр Леонардо ДиКаприо: '{actor_text}'."
        )

    @allure.epic("Глобальный поиск контента")
    @allure.feature("Поиск по имени актера")
    @allure.story("Успешный поиск фильмографии актёра")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_wrong_layout_correction(self):
        """Тест-кейс №3: Автоматическое исправление неверной раскладки"""
        with allure.step("Открыть главную страницу Кинопоиска"):
            self.main_page.open()

        with allure.step("Ввод названия фильма на латинице"):
            self.main_page.search_for("Bynthcntkkfh")

        with allure.step("Успешный поиск названия фильма"):
            suggest_text = self.search_results_page.get_suggest_block_text()
        self.assertIn("Интерстеллар", suggest_text)
        print(f"[ASSERT] Проверка прошла успешно. Запрос исправлен. '{suggest_text}'.")

    @allure.epic("Выбор фильмов по фильтру")
    @allure.feature("Выбор фильма из 250 лучших фильмов по фильтру")
    @allure.story("Успешная фильтрация фильмов")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_for_the_best(self):
        """Тест-кейс №4: Выбор фильма из 250 лучших фильмов по фильтру"""
        with allure.step("Открыть главную страницу Кинопоиска"):
            self.main_page.open()
            self.main_page.click_films_navigation()
        with allure.step("Формирование запросов по топ 250, стране, жанру"):
            self.top250_page.open_top_250_list()
            self.top250_page.select_country_russia()
            self.top250_page.select_genre_military()

        with allure.step("Успешная филтрация по топ 250, стране, жанру"):
            current_year_val = self.top250_page.get_selected_year_text()
            self.assertEqual(
                current_year_val,
                "Все годы",
                f"Ожидалось 'Все годы', но фактически отображается: '{current_year_val}'",
            )
        with allure.step("Выбор года"):
            self.top250_page.select_years_2020_2029()
        with allure.step("Проверка соответствия названия фильма ожиданиям"):
            title_element = self.top250_page.get_target_movie_element()
            self.assertTrue(
                title_element.is_displayed(),
                "Фильм 'Подольские курсанты' найден в DOM, но не отображается!",
            )
            self.assertIn("Подольские курсанты", title_element.text)
        with allure.step("Проверка описания под названием фильма"):
            movie_elements = self.top250_page.get_all_movie_info_elements()
            for index, movie in enumerate(movie_elements):
                movie_text = movie.text

                # Если строка рассказывает про актеров, а не про страну, просто пропускаем её
                if "В ролях:" in movie_text and "Россия" not in movie_text:
                    continue
                self.assertIn(
                    "Россия",
                    movie_text,
                    f"Ошибка в элементе №{index + 1}! Текст элемента: '{movie_text}'",
                )

        print(
            f"[ASSERT] Проверка прошла успешно. Выбран фильм: '{title_element.text}'."
        )

    # =====================================================================
    # ФУНКЦИЯ 2: АВТОРИЗАЦИЯ И ЛИЧНЫЙ ПРОФИЛЬ
    # =====================================================================

    @allure.epic("Авторизация и личный профиль")
    @allure.feature("Списки пользователя")
    @allure.story("Защита добавления в список без авторизации")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_movie_to_watchlist(self):
        """Тест-кейс №5: Попытка добавления фильма в список 'Буду смотреть' без авторизации"""
        with allure.step("Открыть страницу фильма напрямую"):
            self.movie_page.open_movie("258687")

        with allure.step("Кликнуть по кнопке 'Буду смотреть'"):
            self.movie_page.click_watchlist_button()

        with allure.step("Ожидать редирект на страницу Яндекс Паспорта"):
            self.auth_profiles_page.wait_for_url_change("passport.yandex")
            current_url = self.auth_profiles_page.get_current_url()

        with allure.step(
            "Проверить наличие домена passport.yandex и параметра retpath"
        ):
            self.assertIn("passport.yandex", current_url)
            self.assertIn("retpath", current_url)

    # =====================================================================
    # ФУНКЦИЯ 3: ОНЛАЙН-КИНОТЕАТР
    # =====================================================================
    @allure.epic("Авторизация и личный профиль")
    @allure.feature("Списки пользователя")
    @allure.story("Защита попытки просмотра платного контента без подписки")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_play_premium_content_without_subscription(self):
        """Тест-кейс №6: Попытка просмотра платного контента без подписки"""
        # Открываем фильм "Джентльмены" (ID: 1143242)
        with allure.step("Открываем фильм 'Джентльмены' (ID: 1143242)"):
            self.movie_page.open_movie("1143242")

        with allure.step("Кликнуть по кнопке 'Смотреть'"):
            self.movie_page.click_watch_button()

        with allure.step("Ожидать редирект на страницу Яндекс Паспорта"):
            self.auth_profiles_page.wait_for_url_change("passport.yandex")
            current_url = self.auth_profiles_page.get_current_url()

        with allure.step("Убеждаемся, что в URL присутствует домен Яндекс Паспорта"):
            self.assertIn(
                "passport.yandex",
                current_url,
                f"Пользователь не был перенаправлен на Яндекс Паспорт. Текущий URL: {current_url}",
            )

        with allure.step(
            "Убеждаемся, что в URL сохранен обратный путь (retpath) на Кинопоиск"
        ):
            self.assertIn(
                "retpath",
                current_url,
                f"В URL отсутствует параметр retpath для возврата на Кинопоиск. Текущий URL: {current_url}",
            )

        print(
            f"[ASSERT] Система успешно заблокировала действие и перенаправила на авторизацию: '{current_url}'."
        )


if __name__ == "__main__":
    unittest.main()
