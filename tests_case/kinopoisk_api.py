import requests


class BaseClient:
    """Базовый клиент, который отвечает за авторизацию и отправку сырых запросов."""

    def __init__(
        self, api_key: str, base_url: str = "https://kinopoiskapiunofficial.tech"
    ):
        self.base_url = base_url
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }


    def get(self, endpoint: str, params: dict | None = None) -> requests.Response:
        """Внутренний метод для отправки GET-запросов (чтобы не дублировать код)."""
        url = f"{self.base_url}{endpoint}"
        return requests.get(url, headers=self.headers, params=params)


class FilmsComponent:
    """Компонент для работы с эндпоинтами фильмов (/api/v2.2/films)."""

    def __init__(self, client: BaseClient):
        self.client = client
        self.version_path = "/api/v2.2/films"

    def get_by_id(self, film_id: int) -> requests.Response:
        """Получить фильм по ID: /api/v2.2/films/{id}"""
        return self.client.get(f"{self.version_path}/{film_id}")

    def get_top(
        self, type_: str = "TOP_250_BEST_FILMS", page: int = 1
    ) -> requests.Response:
        """Получить топ фильмов: /api/v2.2/films/top"""
        params = {"type": type_, "page": page}
        return self.client.get(f"{self.version_path}/top", params=params)

    def get_box_office(self, film_id: int) -> requests.Response:
        """Получение данных о бюджете и сборах фильма api/v2.2/films/ID/box_office"""
        return self.client.get(f"{self.version_path}/{film_id}/box_office")

    def get_awards(self, film_id: int) -> requests.Response:
        """Получить данные о наградах и премиях фильма."""
        return self.client.get(f"{self.version_path}/{film_id}/awards")

    def get_collections(
        self, type: str = "LOVE_THEME", page: int = 1
    ) -> requests.Response:
        """Получить список фильмов из различных топов или коллекций
        /api/v2.2/films/collections?type=LOVE_THEME&page=1
        """
        parametrs = {"type": type, "page": page}
        return self.client.get(f"{self.version_path}/collections", parametrs)

    def gef_filters(self) -> requests.Response:
        """Получить id стран и жанров для использования в /api/v2.2/films/filters"""
        return self.client.get(f"{self.version_path}/filters")

    def get_films_genres(self, genres: int = 1) -> requests.Response:
        """Получить список фильмов по жанру /api/v2.2/films?genres=5"""
        parametrs = {"genres": genres}
        return self.client.get(f"{self.version_path}", parametrs)


class StaffComponent:
    """Компонент для работы с актерами и создателями (/api/v1/staff)."""

    def __init__(self, client: BaseClient):
        self.client = client

    def get_staff_by_id(self, staff_id: int) -> requests.Response:
        """Получить данные актера по ID: /api/v1/staff/{id}"""
        return self.client.get(f"/api/v1/staff/{staff_id}")


class Films_one_Component:
    """Компонент для работы со списками и сиквелами (/api/v1/films)."""

    def __init__(self, client: BaseClient):
        self.client = client
        self.endpoint_path = "/api/v2.1/films"

    def get_film_search_by_keyword(
        self, keyword: str, page: int = 1
    ) -> requests.Response:
        """Получить фильм по ключевым словам"""
        parameters = {"keyword": keyword, "page": page}
        return self.client.get(f"{self.endpoint_path}/search-by-keyword", parameters)


class MediaComponent:
    """Компонент для работы с медиа-новостями (/api/v1/media_posts)."""

    def __init__(self, client: BaseClient):
        self.client = client
        self.endpoint_path = "/api/v1/media_posts"

    def get_media_posts(self, page: int = 1) -> requests.Response:
        """
        Получить список медиа-новостей.
        Параметры:
            page (int): Номер страницы для пагинации (по умолчанию 1).
        """
        params = {"page": page}
        return self.client.get(self.endpoint_path, params=params)


class KinopoiskAPI:
    """Финальный класс, объединяющий все эндпоинты в единый интерфейс."""

    def __init__(self, api_key: str):
        # Инициализируем базовое соединение
        self.client = BaseClient(api_key=api_key)

        # Подключаем компоненты (наши "страницы" из Page Object)
        self.films = FilmsComponent(self.client)  #  эндпоинт фильмов
        self.staff = StaffComponent(
            self.client
        )  #  эндпоинт для работы с данными об актерах, режиссерах и т.д.
        self.media = MediaComponent(self.client)  #  эндпоинт новостей
        self.films_one = Films_one_Component(
            self.client
        )  # эндпоинт получить список фильмов по ключевым словам
        # получить сиквелы и приквелы для фильма по
        # kinopoisk film id
