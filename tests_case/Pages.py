from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LocatorType = tuple[str, str]


class BasePage:
    """Базовый класс для всех страниц, содержащий общие методы работы с веб-элементами."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver: WebDriver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 40)
        self.base_url: str = "https://kinopoisk.ru"

    def open(self, url: str = "") -> None:
        self.driver.get(f"{self.base_url}{url}")

    def find(self, locator: LocatorType) -> WebElement:
        return self.driver.find_element(*locator)

    def wait_for_element(self, locator: LocatorType) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_clickable(self, locator: LocatorType) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click_via_js(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    def scroll_to_element(self, element: WebElement) -> None:
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )


class MainPage(BasePage):
    """Главная страница Кинопоиска."""

    SEARCH_INPUT: LocatorType = (
        By.CSS_SELECTOR,
        "input[placeholder='Фильмы, сериалы, персоны']",
    )
    NAV_FILMS_LINK: LocatorType = (By.XPATH, "//a[contains(., 'Фильмы')]")

    def search_for(self, text: str) -> None:
        """Ввод текста в поисковую строку и нажатие Enter."""
        search_input: WebElement = self.find(self.SEARCH_INPUT)
        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)

    def click_films_navigation(self) -> None:
        """Переход в раздел 'Фильмы' через верхнее навигационное меню."""
        films_link: WebElement = self.wait_for_clickable(self.NAV_FILMS_LINK)
        films_link.send_keys(Keys.ENTER)


class SearchResultsPage(BasePage):
    """Страница результатов поиска / Исправления раскладки."""

    FIRST_RESULT: LocatorType = (By.CSS_SELECTOR, "span[data-tid='45f60312']")
    ACTOR_HEADING: LocatorType = (By.XPATH, "//span[text()='Леонардо ДиКаприо']")
    SUGGEST_BLOCK: LocatorType = (By.XPATH, "//span[text()='Интерстеллар']")

    def get_first_result_text(self) -> str:
        return self.wait_for_element(self.FIRST_RESULT).text

    def get_actor_heading_text(self) -> str:
        return self.wait_for_element(self.ACTOR_HEADING).text

    def get_suggest_block_text(self) -> str:
        return self.wait_for_element(self.SUGGEST_BLOCK).text


class Top250Page(BasePage):
    """Страница ТОП-250 фильмов с фильтрами."""

    TOP_250_LINK: LocatorType = (By.XPATH, '//span[text()="250 лучших фильмов"]')
    COUNTRY_FILTER_BTN: LocatorType = (By.CSS_SELECTOR, 'button[aria-label="Страны"]')
    RUSSIA_OPTION: LocatorType = (By.XPATH, '//*[text()="Russia" or text()="Россия"]')
    GENRE_FILTER_BTN: LocatorType = (By.XPATH, "//button[@aria-label='Жанры']")
    MILITARY_GENRE_OPTION: LocatorType = (By.XPATH, '//*[text()="Военные"]')
    YEAR_FILTER_BTN: LocatorType = (By.CSS_SELECTOR, 'button[aria-label="Годы"]')
    YEAR_SELECTED_VAL: LocatorType = (
        By.XPATH,
        '//button[@aria-label="Годы"]//span[contains(@class, "styles_selectedItem")]',
    )
    YEAR_2020_OPTION: LocatorType = (By.XPATH, '//*[text()="2020-2029"]')
    TARGET_MOVIE_TITLE: LocatorType = (By.XPATH, '//*[text()="Подольские курсанты"]')
    MOVIE_INFO_ROWS: LocatorType = (
        By.CSS_SELECTOR,
        "span[class^='desktop-list-main-info_truncatedText']",
    )

    def open_top_250_list(self) -> None:
        element: WebElement = self.wait_for_clickable(self.TOP_250_LINK)
        self.click_via_js(element)

    def select_country_russia(self) -> None:
        btn: WebElement = self.wait_for_clickable(self.COUNTRY_FILTER_BTN)
        self.scroll_to_element(btn)
        btn.click()
        self.wait_for_clickable(self.RUSSIA_OPTION).click()

    def select_genre_military(self) -> None:
        self.wait_for_clickable(self.GENRE_FILTER_BTN).click()
        self.wait_for_clickable(self.MILITARY_GENRE_OPTION).click()

    def get_selected_year_text(self) -> str:
        return self.find(self.YEAR_SELECTED_VAL).text

    def select_years_2020_2029(self) -> None:
        self.wait_for_clickable(self.YEAR_FILTER_BTN).click()
        year_opt: WebElement = self.wait_for_clickable(self.YEAR_2020_OPTION)
        self.click_via_js(year_opt)

    def get_target_movie_element(self) -> WebElement:
        return self.wait_for_element(self.TARGET_MOVIE_TITLE)

    def get_all_movie_info_elements(self) -> list[WebElement]:
        # Используем встроенный list вместо typing.List
        result: list[WebElement] = self.wait.until(
            EC.visibility_of_all_elements_located(self.MOVIE_INFO_ROWS)
        )
        return result


class MoviePage(BasePage):
    """Страница конкретного фильма Кинопоиска."""

    WATCHLIST_BTN: LocatorType = (By.XPATH, "//button[@title='Буду смотреть']")
    WATCH_MOVIE_BTN: LocatorType = (By.CSS_SELECTOR, "span[data-tid='6cb8d12f']")

    def open_movie(self, movie_id: str) -> None:
        """Открывает страницу фильма по его ID."""
        self.open(f"/film/{movie_id}/")

    def click_watchlist_button(self) -> None:
        """Нажимает кнопку добавления в список 'Буду смотреть'."""
        self.wait_for_clickable(self.WATCHLIST_BTN).click()

    def wait_until_watchlist_is_pressed(self) -> str:
        """Ждет, пока кнопка перейдет в состояние 'нажата', и возвращает значение атрибута."""
        btn: WebElement = self.wait_for_element(self.WATCHLIST_BTN)
        self.wait.until(lambda d: btn.get_attribute("aria-pressed") == "true")
        return str(btn.get_attribute("aria-pressed"))

    def click_watch_button(self) -> None:
        """Нажимает кнопку 'Смотреть'."""
        self.wait_for_clickable(self.WATCH_MOVIE_BTN).click()


class AuthProfilesPage(BasePage):
    """Страница выбора профилей Плюса или авторизации Яндекса после редиректа."""

    def wait_for_url_change(self, part_url: str = "profiles") -> None:
        """Ожидает, пока текущий URL будет содержать указанную часть."""
        self.wait.until(lambda d: part_url in d.current_url)

    def get_current_url(self) -> str:
        """Возвращает текущий URL."""
        return self.driver.current_url

    def get_page_source(self) -> str:
        """Возвращает HTML-код страницы."""
        return self.driver.page_source
